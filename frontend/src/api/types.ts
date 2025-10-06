export interface ScriptRequest {
  topic: string;
  duration_minutes: number;
  tone: string;
}

export interface ScriptScene {
  scene_id: string;
  title: string;
  visual: string;
  narration: string;
  duration_seconds: number;
}

export interface Script {
  script_id: string;
  topic: string;
  duration_minutes: number;
  scenes: ScriptScene[];
  created_at: string;
}

export interface SceneAudio {
  scene_id: string;
  audio_url: string;
  duration_seconds?: number | null;
}

export interface ScriptResponse {
  script: Script;
  audio: SceneAudio[];
}

export interface VideoMetadata {
  video_id: string;
  script_id: string;
  title: string;
  status: string;
  created_at: string;
  storage_path?: string | null;
  thumbnail_url?: string | null;
}
