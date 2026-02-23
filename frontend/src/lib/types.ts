export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sql?: string;
  data?: Record<string, any>[];
  chart?: Record<string, any>;
}

export interface ChatResponse {
  text: string;
  sql?: string;
  data?: Record<string, any>[];
  chart_spec?: Record<string, any>;
  error?: string;
}

export interface DataSummary {
  total_projects: number;
  total_countries: number;
  total_credits_issued: number;
  total_credits_retired: number;
  quadrant_distribution: Record<string, number>;
  velocity_stats: {
    average: number;
    max: number;
    min: number;
  };
  momentum_stats: {
    average: number;
    max: number;
    min: number;
  };
}

export interface SuggestedQuestionsData {
  categories: Record<string, string[]>;
}

export interface Project {
  project_id: number;
  name: string;
  country: string;
  velocity: number;
  momentum: number;
  quadrant: string;
}
