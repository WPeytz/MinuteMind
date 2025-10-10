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

        <div v-if="rendering && !video" class="flex items-center justify-center gap-3 rounded-lg border border-brand-400/30 bg-brand-900/20 px-6 py-4 text-brand-300">
          <span class="h-2 w-2 animate-ping rounded-full bg-brand-400"></span>
          <span class="text-sm font-medium">Rendering video…</span>
        </div>
      </div>
    </Transition>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { RouterLink } from "vue-router";

import { generateScript, renderVideo } from "@/api/client";
import type { ScriptRequest, ScriptResponse, VideoMetadata } from "@/api/types";
import TopicForm from "@/components/TopicForm.vue";

const generating = ref(false);
const rendering = ref(false);
const scriptResponse = ref<ScriptResponse | null>(null);
const video = ref<VideoMetadata | null>(null);
const error = ref<string | null>(null);

const onSubmit = async (payload: ScriptRequest) => {
  generating.value = true;
  rendering.value = true;
  video.value = null;
  error.value = null;
  try {
    scriptResponse.value = await generateScript(payload);
    // Automatically render video after script generation
    if (scriptResponse.value) {
      video.value = await renderVideo(scriptResponse.value);
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Failed to generate script or render video";
    scriptResponse.value = null;
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
