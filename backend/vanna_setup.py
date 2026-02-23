"""
Setup for text-to-SQL on Verra carbon credit database using OpenAI.
"""

import os
import sqlite3
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from training_data import DDL_STATEMENTS, SAMPLE_QUERIES, BUSINESS_DOCUMENTATION

# Load environment variables
load_dotenv()

DB_PATH = Path(__file__).parent.parent / "verra.db"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not set in .env file")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


class VannaVerra:
    """Simple text-to-SQL using OpenAI API and ChromaDB for context."""
    
    def __init__(self, model: str = "gpt-4o", api_key: str = None, chroma_path: str = None):
        self.model = model
        self.api_key = api_key
        self.context = self._build_context()
    
    def _build_context(self) -> str:
        """Build context from DDL and sample queries."""
        context = "# DATABASE SCHEMA\n\n"
        for ddl in DDL_STATEMENTS:
            context += ddl + "\n\n"
        
        context += "# SAMPLE QUERIES AND QUESTIONS\n\n"
        for question, query in SAMPLE_QUERIES:
            context += f"Q: {question}\nSQL: {query}\n\n"
        
        context += "# BUSINESS CONTEXT\n\n"
        context += BUSINESS_DOCUMENTATION
        
        return context
    
    def generate_sql(self, question: str) -> str:
        """Generate SQL from natural language question."""
        messages = [
            {
                "role": "system",
                "content": f"""You are a SQL expert. Given a question, generate a valid SQLite SQL query.
Only respond with the SQL query, no explanations.

{self.context}"""
            },
            {
                "role": "user",
                "content": question
            }
        ]
        
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0,
            max_completion_tokens=500
        )
        
        sql = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if sql.startswith("```"):
            sql = "\n".join(sql.split("\n")[1:-1])
        return sql
    
    def generate_plotly_code(self, question: str, sql: str, df_metadata: str) -> str:
        """Generate Plotly code for visualization."""
        messages = [
            {
                "role": "system",
                "content": """You are a Plotly expert. Given a question, SQL query, and data metadata, 
generate Plotly.js code to visualize the data. Return only valid JSON that can be used with Plotly.
Example format: {"data": [...], "layout": {...}}"""
            },
            {
                "role": "user",
                "content": f"""Question: {question}
SQL: {sql}
Data Metadata: {df_metadata}

Generate Plotly JSON spec for visualization."""
            }
        ]
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0,
                max_completion_tokens=1000
            )
            
            chart_code = response.choices[0].message.content.strip()
            # Try to parse as JSON to validate
            if chart_code.startswith("```"):
                chart_code = "\n".join(chart_code.split("\n")[1:-1])
            json.loads(chart_code)
            return chart_code
        except:
            return None
    
    def train(self, **kwargs):
        """Placeholder for training (not needed with direct OpenAI)."""
        pass

    def generate_user_friendly_response(
        self, question: str, sql: str, data: list, columns: list
    ) -> tuple[str, dict | None]:
        """
        Generate a conversational response AND let the LLM decide if a chart would help.
        Returns (friendly_text, chart_spec or None).
        """
        data_sample = data[:15] if data else []
        data_summary = json.dumps(data_sample, default=str)[:3000]
        row_count = len(data)

        messages = [
            {
                "role": "system",
                "content": """You are a friendly carbon credit analyst. Turn query results into a conversational response AND decide if a chart would help.

CHART DECISION - Include a chart when:
- User asked to compare things (by country, type, quadrant)
- Data has rankings, top-N lists (bar chart works well)
- Distributions, proportions (pie or bar)
- Trends over time (line chart)
- Numeric comparisons (velocity, momentum, counts)

DO NOT include a chart when:
- Single record or very few rows with no clear viz value
- Simple list of names/IDs with no numeric dimension to plot
- User asked a yes/no or factual question

If including a chart: Build Plotly spec from the ACTUAL data. Example for bar chart:
{"data": [{"x": ["Country A", "Country B", "Country C"], "y": [120, 85, 90], "type": "bar", "name": "Projects"}], "layout": {"title": "Projects by Country", "xaxis": {"title": "Country"}, "yaxis": {"title": "Count"}}}
- Extract x (labels) and y (values) from the data sample - use real column values
- Limit to top 10-12 items for readability
- type: "bar" for rankings, "pie" for proportions (pie needs "values" and "labels" instead of x/y)

Response: Warm, 2-4 paragraphs, plain language. Never mention SQL."""
            },
            {
                "role": "user",
                "content": f"""Question: {question}

Query returned {row_count} rows.
Columns: {columns}
Data (sample): {data_summary}

Return valid JSON only:
{{"response": "your conversational answer", "include_chart": true or false, "chart": null or {{"data": [{{"x": [], "y": [], "type": "bar"}}], "layout": {{"title": ""}}}}}}
When include_chart is false use null for chart. When true, chart needs data array and layout object.""",
            },
        ]

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_completion_tokens=1500,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response")
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            parsed = json.loads(content)

            text = parsed.get("response", "")
            include_chart = parsed.get("include_chart", False)
            chart_spec = parsed.get("chart") if include_chart else None

            # Validate chart has data and layout
            if chart_spec and isinstance(chart_spec, dict):
                data_traces = chart_spec.get("data", [])
                layout = chart_spec.get("layout", {})
                if data_traces and layout:
                    return (text, chart_spec)
            return (text, None)

        except Exception as e:
            print(f"Combined response generation failed: {e}")
            # Fallback: text only, try legacy chart gen
            if data:
                first = data[0]
                name = first.get("Name", first.get("name", "—"))
                country = first.get("Country_Area", first.get("country", "—"))
                text = f"I found **{row_count}** results.\n\nA standout: **{name}** ({country})—check the data below for details."
            else:
                text = f"I found {row_count} results for your query. See the data below for details."
            return (text, None)


def setup_vanna() -> VannaVerra:
    """Initialize Vanna for the Verra carbon credit database."""
    print(f"Initializing Vanna with {LLM_MODEL}...")
    vn = VannaVerra(
        model=LLM_MODEL,
        api_key=OPENAI_API_KEY,
        chroma_path=str(Path(__file__).parent.parent / "chroma_db"),
    )
    print("Vanna initialization complete!")
    return vn


def get_vanna() -> VannaVerra:
    """Get or create a Vanna instance."""
    vn = VannaVerra(
        model=LLM_MODEL,
        api_key=OPENAI_API_KEY,
        chroma_path=str(Path(__file__).parent.parent / "chroma_db"),
    )
    return vn


def execute_query(vn: VannaVerra, question: str) -> dict:
    """Execute a natural language question through Vanna."""
    try:
        # Generate SQL from question
        print(f"Question: {question}")
        sql = vn.generate_sql(question)
        print(f"Generated SQL: {sql}")

        # Execute SQL
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()

        # Convert to list of dicts
        data = [dict(zip(columns, row)) for row in results]

        # Generate friendly response + LLM decides if chart helps and generates it
        friendly_text, chart_spec = vn.generate_user_friendly_response(
            question=question,
            sql=sql,
            data=data,
            columns=columns,
        )

        # Fallback: if LLM didn't produce a chart but we have plottable data, try legacy
        if not chart_spec and data and len(data) > 1:
            try:
                chart_code = vn.generate_plotly_code(
                    question=question,
                    sql=sql,
                    df_metadata=str({"columns": columns, "sample": data[:10]})
                )
                if chart_code:
                    chart_spec = json.loads(chart_code)
            except Exception as e:
                print(f"Fallback chart generation: {e}")

        return {
            "success": True,
            "text": friendly_text,
            "sql": sql,
            "data": data,
            "chart_spec": chart_spec,
            "error": None,
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            "success": False,
            "sql": None,
            "data": None,
            "chart_spec": None,
            "error": str(e),
        }


if __name__ == "__main__":
    # Test setup
    print("Setting up Vanna...")
    vn = setup_vanna()

    # Test a query
    result = execute_query(vn, "Which projects are heating up?")
    print(f"\nResult: {result}")
