<template>
  <section class="space-y-10">
    <header class="space-y-3">
      <p class="text-sm uppercase tracking-widest text-brand-300/80">AI Assisted Workflows</p>
      <h1 class="text-4xl font-semibold text-white">MinuteMind videos</h1>
      <p class="max-w-2xl text-sm text-slate-300">
        What do you want to learn?
      </p>
    </header>

    <TopicForm :busy="generating" @submit="onSubmit" />

    <Transition name="fade">
      <div v-if="error" class="rounded-lg border border-red-400/30 bg-red-400/10 p-4 text-sm text-red-100">
        {{ error }}
      </div>
    </Transition>

    <Transition name="fade">
      <div v-if="hasScript" class="space-y-6">
        <div v-if="!video" class="flex items-center justify-between">
          <h2 class="text-2xl font-semibold text-white">Script Generated</h2>
          <span class="text-xs uppercase tracking-wide text-slate-400">
            {{ scenes.length }} scenes • ~{{ scriptDuration }} min
          </span>
        </div>

        <Transition name="fade">
          <div v-if="video" class="space-y-4">
            <h2 class="text-2xl font-semibold text-white">Your Video</h2>
            <div class="overflow-hidden rounded-xl border border-white/10 bg-slate-900/60">
              <video
                :src="video.storage_path ?? ''"
                controls
                class="w-full aspect-video bg-black"
              >
                Your browser does not support the video tag.
              </video>
            </div>
            <div class="flex items-center justify-between text-sm text-slate-300">
              <p>{{ video.title }}</p>
              <a
                :href="video.storage_path ?? '#'"
                target="_blank"
                rel="noreferrer"
                class="text-brand-300 hover:text-brand-200"
              >
                Open in new tab →
              </a>
            </div>
          </div>
        </Transition>

        <button
          v-if="!video"
          class="w-full rounded-lg bg-brand-500 px-6 py-3 text-base font-semibold text-white shadow-lg shadow-brand-900/60 transition hover:bg-brand-400 disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="rendering"
          @click="onRenderVideo"
        >
          <span v-if="rendering" class="flex items-center justify-center gap-2">
            <span class="h-2 w-2 animate-ping rounded-full bg-white"></span>
            Rendering video…
          </span>
          <span v-else>Generate Video</span>
        </button>
      </div>
    </Transition>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

import { generateScript, renderVideo } from "@/api/client";
import type { SceneAudio, ScriptRequest, ScriptResponse, VideoMetadata } from "@/api/types";
import TopicForm from "@/components/TopicForm.vue";

const generating = ref(false);
const rendering = ref(false);
const scriptResponse = ref<ScriptResponse | null>(null);
const video = ref<VideoMetadata | null>(null);
const error = ref<string | null>(null);

const hasScript = computed(() => scriptResponse.value !== null);
const scenes = computed(() => scriptResponse.value?.script.scenes ?? []);
const scriptDuration = computed(() => scriptResponse.value?.script.duration_minutes ?? 0);

const audioFor = (sceneId: string): SceneAudio[] => {
  return (scriptResponse.value?.audio ?? []).filter((audio) => audio.scene_id === sceneId);
};

const onSubmit = async (payload: ScriptRequest) => {
  generating.value = true;
  rendering.value = false;
  video.value = null;
  error.value = null;
  try {
    scriptResponse.value = await generateScript(payload);
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Failed to generate script";
    scriptResponse.value = null;
  } finally {
    generating.value = false;
  }
};

const onRenderVideo = async () => {
  if (!scriptResponse.value) return;
  rendering.value = true;
  error.value = null;
  try {
    video.value = await renderVideo(scriptResponse.value);
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Failed to render video";
  } finally {
    rendering.value = false;
  }
};
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
