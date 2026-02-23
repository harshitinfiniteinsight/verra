import axios from "axios";
import type {
  ChatResponse,
  DataSummary,
  SuggestedQuestionsData,
  Project,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function sendMessage(
  message: string,
  history: any[] = []
): Promise<ChatResponse> {
  const response = await api.post("/api/chat", {
    message,
    history,
  });
  return response.data;
}

export async function getDataSummary(): Promise<DataSummary> {
  const response = await api.get("/api/data/summary");
  return response.data;
}

export async function getSuggestedQuestions(): Promise<SuggestedQuestionsData> {
  const response = await api.get("/api/data/suggestions");
  return response.data;
}

export async function getHotProjects(limit: number = 10): Promise<{
  projects: Project[];
}> {
  const response = await api.get("/api/data/hot-projects", {
    params: { limit },
  });
  return response.data;
}

export async function getEmergingProjects(limit: number = 10): Promise<{
  projects: Project[];
}> {
  const response = await api.get("/api/data/emerging-projects", {
    params: { limit },
  });
  return response.data;
}

export async function getSlowinProjects(limit: number = 10): Promise<{
  projects: Project[];
}> {
  const response = await api.get("/api/data/slowing-projects", {
    params: { limit },
  });
  return response.data;
}
