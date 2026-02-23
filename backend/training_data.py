"""
Training data for Vanna AI - DDL, sample SQL queries, and business documentation.
This trains the Vanna framework to better understand the Verra carbon credit domain.
"""

# DDL (Database schema) - helps Vanna understand table structure
DDL_STATEMENTS = [
    """
    CREATE TABLE vcus (
        Issuance_Date DATE COMMENT 'Date when VCUs were issued',
        Sustainable_Development_Goals TEXT COMMENT 'Comma-separated SDG numbers',
        Vintage_Start DATE COMMENT 'Start of the vintage period',
        Vintage_End DATE COMMENT 'End of the vintage period',
        ID INTEGER COMMENT 'Unique project ID',
        Name TEXT COMMENT 'Project name',
        Country_Area TEXT COMMENT 'Country where project is located',
        Project_Type TEXT COMMENT 'Type of project (e.g., AFOLU, Energy industries)',
        Methodology TEXT COMMENT 'Methodology used for verification',
        Total_Vintage_Quantity INTEGER COMMENT 'Total VCUs for this vintage',
        Quantity_Issued INTEGER COMMENT 'Number of VCUs issued',
        Serial_Number TEXT COMMENT 'Unique serial number for this batch',
        Additional_Certifications TEXT COMMENT 'Additional certifications (CORSIA, Article 6, etc)',
        Retirement_Cancellation_Date DATE COMMENT 'When credits were retired',
        Retirement_Beneficiary TEXT COMMENT 'Entity that retired the credits (intermediary or end-buyer)',
        Retirement_Reason TEXT COMMENT 'Reason for retirement',
        Retirement_Details TEXT COMMENT 'Additional retirement details'
    )
    """,
    """
    CREATE TABLE project_summary (
        ID INTEGER PRIMARY KEY,
        Name TEXT,
        Country_Area TEXT,
        Project_Type TEXT,
        Methodology TEXT,
        num_issuances INTEGER,
        num_retirements INTEGER,
        total_vintage_quantity INTEGER,
        total_quantity_issued INTEGER,
        total_retired INTEGER,
        first_issuance_date DATE,
        last_issuance_date DATE,
        unique_retirement_beneficiaries INTEGER
    )
    """,
    """
    CREATE TABLE project_metrics (
        ID INTEGER PRIMARY KEY,
        recent_90d_count INTEGER COMMENT 'Number of retirement events in last 90 days',
        prior_90d_count INTEGER COMMENT 'Number of retirement events in prior 90-day period',
        recent_90z REAL COMMENT 'Z-score of recent 90-day activity',
        delta_z REAL COMMENT 'Z-score of change in activity (momentum)',
        velocity REAL COMMENT 'Normalized activity intensity: (recent_90 / qty_issued) * 10000',
        quadrant TEXT COMMENT 'Quadrant classification: Hot, Emerging, Stable, or Dormant'
    )
    """,
    """
    CREATE TABLE retirement_beneficiaries (
        ID INTEGER,
        Retirement_Beneficiary TEXT,
        retirement_count INTEGER,
        quantity_retired INTEGER
    )
    """,
]

# Sample SQL queries - teaches Vanna the kinds of questions users ask
SAMPLE_QUERIES = [
    # Basic aggregations
    ("Which country has the most retirements?",
     "SELECT Country_Area, SUM(total_retired) as total_retired FROM project_summary GROUP BY Country_Area ORDER BY total_retired DESC LIMIT 10"),
    
    ("Show me issuance trends over time",
     "SELECT DATE_TRUNC(Issuance_Date, 'month') as month, COUNT(*) as num_issuances, SUM(Quantity_Issued) as total_issued FROM vcus GROUP BY month ORDER BY month"),
    
    ("What are the top 10 projects by quantity issued?",
     "SELECT Name, Country_Area, total_quantity_issued FROM project_summary ORDER BY total_quantity_issued DESC LIMIT 10"),
    
    # Momentum & Velocity queries
    ("Which projects are heating up?",
     "SELECT ps.Name, ps.Country_Area, pm.velocity, pm.delta_z, pm.quadrant FROM project_summary ps JOIN project_metrics pm ON ps.ID = pm.ID WHERE pm.quadrant = 'Hot' ORDER BY pm.velocity DESC LIMIT 20"),
    
    ("Which projects are slowing down?",
     "SELECT ps.Name, ps.Country_Area, pm.velocity, pm.delta_z, pm.quadrant FROM project_summary ps JOIN project_metrics pm ON ps.ID = pm.ID WHERE pm.delta_z < 0 ORDER BY pm.delta_z ASC LIMIT 20"),
    
    ("Where are emerging opportunities in AFOLU projects?",
     "SELECT ps.Name, ps.Country_Area, pm.velocity, pm.delta_z FROM project_summary ps JOIN project_metrics pm ON ps.ID = pm.ID WHERE ps.Project_Type LIKE '%AFOLU%' AND pm.quadrant = 'Emerging' ORDER BY pm.delta_z DESC"),
    
    ("Show the 2x2 matrix of projects by momentum and velocity",
     "SELECT quadrant, COUNT(*) as project_count, AVG(velocity) as avg_velocity, AVG(delta_z) as avg_momentum FROM project_metrics GROUP BY quadrant"),
    
    # Intermediary analysis
    ("Who are the top retirement beneficiaries?",
     "SELECT Retirement_Beneficiary, COUNT(*) as retirement_count, SUM(Quantity_Issued) as total_retired FROM vcus WHERE Retirement_Beneficiary IS NOT NULL AND Retirement_Beneficiary != '' GROUP BY Retirement_Beneficiary ORDER BY retirement_count DESC LIMIT 20"),
    
    ("Show intermediaries retiring our project's credits",
     "SELECT rb.Retirement_Beneficiary, rb.retirement_count, rb.quantity_retired FROM retirement_beneficiaries rb WHERE rb.ID = ? ORDER BY rb.retirement_count DESC"),
    
    # Supply and demand
    ("Which projects can we warehouse at lower prices?",
     "SELECT ps.Name, ps.Country_Area, pm.velocity, pm.delta_z, ps.total_retired FROM project_summary ps JOIN project_metrics pm ON ps.ID = pm.ID WHERE pm.velocity > (SELECT AVG(velocity) FROM project_metrics) ORDER BY pm.velocity DESC"),
    
    # Project deep dives
    ("Show all retirement events for project X",
     "SELECT Issuance_Date, Quantity_Issued, Retirement_Cancellation_Date, Retirement_Beneficiary FROM vcus WHERE ID = ? AND Retirement_Cancellation_Date IS NOT NULL ORDER BY Retirement_Cancellation_Date"),
    
    # Aggregations by country/methodology
    ("Compare average momentum by country",
     "SELECT ps.Country_Area, COUNT(*) as projects, AVG(pm.delta_z) as avg_momentum, AVG(pm.velocity) as avg_velocity FROM project_summary ps JOIN project_metrics pm ON ps.ID = pm.ID GROUP BY ps.Country_Area ORDER BY avg_momentum DESC"),
    
    ("Average velocity by project type",
     "SELECT Project_Type, COUNT(*) as projects, AVG(pm.velocity) as avg_velocity FROM project_summary ps JOIN project_metrics pm ON ps.ID = pm.ID GROUP BY ps.Project_Type ORDER BY avg_velocity DESC"),
    
    # Certification analysis
    ("How many projects have CORSIA certification?",
     "SELECT COUNT(DISTINCT ID) as corsia_projects FROM vcus WHERE Additional_Certifications LIKE '%CORSIA%'"),
    
    ("Article 6 vs non-Article 6 distribution",
     "SELECT CASE WHEN Additional_Certifications LIKE '%Article 6%' THEN 'Article 6' ELSE 'Non-Article 6' END as category, COUNT(DISTINCT ID) as projects FROM vcus GROUP BY category"),
    
    # SDG analysis
    ("Which projects address the most SDGs?",
     "SELECT Name, Sustainable_Development_Goals, LENGTH(Sustainable_Development_Goals) - LENGTH(REPLACE(Sustainable_Development_Goals, ';', '')) + 1 as sdg_count FROM vcus GROUP BY ID ORDER BY sdg_count DESC LIMIT 20"),
    
    # Activity patterns
    ("Recently active projects in the last 90 days",
     "SELECT ps.Name, ps.Country_Area, pm.recent_90d_count as activity_count, pm.velocity FROM project_summary ps JOIN project_metrics pm ON ps.ID = pm.ID WHERE pm.recent_90d_count > 0 ORDER BY pm.velocity DESC LIMIT 20"),
    
    ("Consistently active projects",
     "SELECT ps.Name, ps.Country_Area, pm.recent_90d_count, pm.prior_90d_count, pm.delta_z FROM project_summary ps JOIN project_metrics pm ON ps.ID = pm.ID WHERE pm.recent_90d_count > 0 AND pm.prior_90d_count > 0 AND pm.delta_z BETWEEN -0.5 AND 0.5 ORDER BY pm.velocity DESC"),
]

# Business documentation - context about the domain
BUSINESS_DOCUMENTATION = """
VERRA CARBON CREDIT SYSTEM (VCU) - DOMAIN CONTEXT

1. WHAT IS A VCU?
   A Verified Carbon Unit (VCU) represents one metric ton of CO2 equivalent that has been
   reduced or sequestered by a carbon offset project. VCUs are issued by Verra (formerly
   VCS) after verification and validation by accredited auditors.

2. KEY TERMINOLOGY:
   - Issuance: When VCUs are created and first issued for a verified project.
   - Vintage: The period during which emissions reductions or carbon sequestration occurred.
   - Retirement: When VCUs are permanently removed from circulation (used to offset emissions).
   - Quantity Issued: Number of VCUs issued in a particular batch/issuance.
   - Total Vintage Quantity: Total potential VCUs for a given project-vintage combination.

3. RETIREMENT & INTERMEDIARIES:
   Retirement Beneficiary = the organization retiring the credits. Can be:
   - End-buyer (company retiring to offset own emissions)
   - Intermediary (broker/aggregator buying then selling to end-buyers)
   - Sembcorp (if we are retiring for our own purposes)
   
   Tracking beneficiaries helps identify intermediaries and end-customers.

4. MOMENTUM METRIC:
   Indicates acceleration/deceleration of project activity over time.
   - Based on 180-day retirement windows split into two 90-day periods.
   - delta_z = z-score of change in activity
   - Positive delta_z = rising activity (heating up)
   - Negative delta_z = falling activity (slowing down)
   - Near zero = stable activity
   
5. VELOCITY METRIC:
   Measures how intensely a project is trading relative to its size.
   - Velocity = (retirements in last 90 days / total credits issued) * 10,000
   - Normalizes across projects so small and large projects are comparable.
   - High velocity = high activity intensity
   - Low velocity = low activity intensity

6. 2X2 QUADRANT CLASSIFICATION:
   
   |                    | HIGH VELOCITY      | LOW VELOCITY       |
   |--------------------|--------------------|--------------------|
   | HIGH MOMENTUM      | HOT                | EMERGING           |
   | (delta_z > 0)      | Immediate trading  | Pre-trade position |
   |                    | opportunities      | Rising interest    |
   |--------------------|--------------------|--------------------|
   | LOW MOMENTUM       | STABLE             | DORMANT            |
   | (delta_z <= 0)     | Predictable supply | Low near-term opp. |
   |                    | Watch for inflect. | Monitor for change |
   |--------------------|--------------------|--------------------|

7. SEMBCORP PROJECTS:
   Projects we own. Goals:
   - Sell at highest margin possible
   - Sell all units (maximize issuance)
   - Sell them as fast as possible (high velocity)

8. NON-SEMBCORP PROJECTS:
   Projects we source from developers/intermediaries. Goals:
   - Identify "hot" projects to warehouse at lower prices
   - Match projects to customer requirements (supply/demand)
   - Track intermediaries to understand market structure

9. CERTIFICATIONS:
   - CORSIA: Carbon Offsetting and Reduction Scheme for International Aviation
   - Article 6: Enables international carbon credit transfers under Paris Agreement
   - These certifications make credits eligible for specific markets

10. PROJECT TYPES:
    - AFOLU: Agriculture, Forestry and Other Land Use
    - Energy industries: Renewable and non-renewable energy projects
    - Waste handling and disposal
    - Fugitive emissions
    - And many others

11. METHODOLOGIES:
    Different verification methodologies (ACM0002, VM0050, AMS-III.AV., etc.)
    indicate the framework used to calculate and verify the carbon reductions.

12. SUCCESS METRICS FOR CHATBOT:
    - Number of high-quality leads generated (projects to talk to)
    - Number of projects identified for warehousing
    - Accuracy of intermediary identification
    - Speed of market intelligence gathering
"""

# Business questions the chatbot should answer
CHATBOT_QUESTIONS = [
    # Momentum & Activity
    "Which projects are heating up?",
    "Which projects are slowing down?",
    "Where are emerging opportunities in [project type]?",
    "Which projects should we talk to developers about?",
    "Which projects are consistently active?",
    
    # Supply-side
    "Show hot projects to warehouse",
    "Which projects have high velocity?",
    "Show projects with rising momentum",
    
    # Market Intelligence
    "Who are the top intermediaries?",
    "Show intermediaries retiring our project's credits",
    "Which end-buyers are active in [region]?",
    "Compare market activity by country",
    
    # Analytics
    "Compare average momentum by country",
    "Average velocity by project type",
    "How many projects have CORSIA certification?",
    "Show SDG distribution",
    
    # Project Deep Dives
    "Show all retirement events for [project name]",
    "Who is retiring credits for [project name]?",
    "What is the retirement pattern for [project name]?",
]

if __name__ == "__main__":
    print(f"DDL Statements: {len(DDL_STATEMENTS)}")
    print(f"Sample Queries: {len(SAMPLE_QUERIES)}")
    print(f"Chatbot Questions: {len(CHATBOT_QUESTIONS)}")
    print("\nTrain Vanna with these materials for best results.")
