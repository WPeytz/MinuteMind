<template>
  <section class="mx-auto max-w-4xl space-y-10">
    <header class="space-y-3 text-center">
      <p class="text-sm uppercase tracking-widest text-brand-300/80">AI Assisted Workflows</p>
      <h1 class="text-4xl font-semibold text-white">MinuteMind videos</h1>
      <p class="mx-auto max-w-2xl text-sm text-slate-300">
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
      <div v-if="rendering || video" class="space-y-6">
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
            <div class="flex items-center justify-between gap-4 text-sm">
              <p class="text-slate-300">{{ video.title }}</p>
              <div class="flex gap-3">
                <RouterLink
                  :to="{ name: 'library' }"
                  class="rounded-lg bg-brand-500 px-4 py-2 font-medium text-white transition hover:bg-brand-400"
                >
                  View in Library
                </RouterLink>
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
          </div>
        </Transition>

        <div v-if="rendering && !video" class="space-y-4 rounded-lg border border-brand-400/30 bg-brand-900/20 px-6 py-6">
          <div class="flex items-center justify-between text-sm">
            <span class="flex items-center gap-2 font-medium text-brand-300">
              <span class="h-2 w-2 animate-ping rounded-full bg-brand-400"></span>
              Generating video…
            </span>
            <span class="text-slate-400">{{ estimatedTime }}</span>
          </div>

          <div class="relative h-2 overflow-hidden rounded-full bg-slate-800">
            <div
              class="h-full bg-gradient-to-r from-brand-500 to-brand-400 transition-all duration-300 ease-out"
              :style="{ width: `${progress}%` }"
            ></div>
          </div>

          <p class="text-center text-xs text-slate-400">{{ progressMessage }}</p>
        </div>
      </div>
    </Transition>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from "vue";
import { RouterLink } from "vue-router";

import { generateScript, renderVideo } from "@/api/client";
import type { ScriptRequest, ScriptResponse, VideoMetadata } from "@/api/types";
import TopicForm from "@/components/TopicForm.vue";

const generating = ref(false);
const rendering = ref(false);
const scriptResponse = ref<ScriptResponse | null>(null);
const video = ref<VideoMetadata | null>(null);
const error = ref<string | null>(null);

// Progress tracking
const progress = ref(0);
const progressMessage = ref("Initializing...");
const startTime = ref<number | null>(null);
const estimatedTotalTime = ref(45); // Estimated total time in seconds
let progressInterval: number | null = null;

const estimatedTime = computed(() => {
  if (!startTime.value) return "~45s";

  const elapsed = (Date.now() - startTime.value) / 1000;
  const remaining = Math.max(0, estimatedTotalTime.value - elapsed);

  if (remaining < 1) return "Almost done...";
  if (remaining < 60) return `~${Math.ceil(remaining)}s`;

  const minutes = Math.floor(remaining / 60);
  const seconds = Math.ceil(remaining % 60);
  return `~${minutes}m ${seconds}s`;
});

const progressStages = [
  { progress: 15, message: "Analyzing topic and generating outline..." },
  { progress: 30, message: "Creating scene descriptions..." },
  { progress: 45, message: "Generating narration script..." },
  { progress: 60, message: "Synthesizing audio..." },
  { progress: 75, message: "Creating visuals..." },
  { progress: 90, message: "Stitching video together..." },
  { progress: 95, message: "Finalizing..." },
];

const startProgressSimulation = () => {
  progress.value = 0;
  startTime.value = Date.now();
  let stageIndex = 0;

  progressMessage.value = progressStages[0].message;

  progressInterval = window.setInterval(() => {
    // Increment progress gradually
    if (progress.value < 95) {
      progress.value += 1;

      // Update message based on progress
      if (stageIndex < progressStages.length - 1 && progress.value >= progressStages[stageIndex + 1].progress) {
        stageIndex++;
        progressMessage.value = progressStages[stageIndex].message;
      }
    }
  }, (estimatedTotalTime.value * 1000) / 95); // Spread progress over estimated time
};

const stopProgressSimulation = () => {
  if (progressInterval !== null) {
    clearInterval(progressInterval);
    progressInterval = null;
  }
  progress.value = 100;
  progressMessage.value = "Complete!";
};

onUnmounted(() => {
  stopProgressSimulation();
});

const onSubmit = async (payload: ScriptRequest) => {
  generating.value = true;
  rendering.value = true;
  video.value = null;
  error.value = null;

  startProgressSimulation();

  try {
    scriptResponse.value = await generateScript(payload);
    // Automatically render video after script generation
    if (scriptResponse.value) {
      video.value = await renderVideo(scriptResponse.value);
    }
    stopProgressSimulation();
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Failed to generate script or render video";
    scriptResponse.value = null;
    stopProgressSimulation();
  } finally {
    generating.value = false;
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
