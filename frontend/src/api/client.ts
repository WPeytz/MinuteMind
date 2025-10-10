import axios from "axios";

import type { ScriptRequest, ScriptResponse, VideoMetadata } from "./types";

const rawBase = import.meta.env.VITE_API_BASE_URL || "/api";
const baseURL = rawBase.endsWith("/") ? rawBase.slice(0, -1) : rawBase;

const api = axios.create({
  baseURL,
  maxRedirects: 5, // Follow redirects
});

export async function generateScript(payload: ScriptRequest): Promise<ScriptResponse> {
  const { data } = await api.post<ScriptResponse>("/scripts/generate", payload);
  return data;
}

export async function renderVideo(payload: ScriptResponse): Promise<VideoMetadata> {
  const { data } = await api.post<VideoMetadata>("/videos/render", payload);
  return data;
}

export async function fetchVideos(): Promise<VideoMetadata[]> {
  const { data } = await api.get<VideoMetadata[]>("/videos/");
  return data;
}

export default api;
