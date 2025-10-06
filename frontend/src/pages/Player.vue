<template>
  <section class="space-y-6">
    <header class="space-y-2">
      <h1 class="text-3xl font-semibold text-white">Playback</h1>
      <p class="text-sm text-slate-300">Preview the stitched output directly in your browser.</p>
    </header>

    <div v-if="loading" class="rounded-lg border border-white/10 bg-slate-900/60 p-6 text-sm text-slate-200">
      Loading video…
    </div>

    <div v-else-if="!source" class="rounded-lg border border-red-400/30 bg-red-400/10 p-6 text-sm text-red-100">
      Could not locate a video for this id.
    </div>

    <div v-else class="space-y-4">
      <video
        class="w-full rounded-xl border border-white/10 bg-black shadow-xl shadow-black/60"
        controls
        :src="source"
      ></video>
      <a
        :href="source"
        target="_blank"
        rel="noreferrer"
        class="inline-flex items-center gap-2 rounded-lg border border-brand-400/60 px-4 py-2 text-sm text-brand-100 hover:bg-brand-500/10"
      >
        Download MP4
      </a>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import { fetchVideos } from "@/api/client";

const route = useRoute();
const loading = ref(true);
const source = ref<string | null>(null);

onMounted(async () => {
  const initial = typeof route.query.src === "string" ? route.query.src : null;
  if (initial) {
    source.value = initial;
    loading.value = false;
    return;
  }

  try {
    const catalog = await fetchVideos();
    const match = catalog.find((video) => video.video_id === route.params.id);
    source.value = match?.storage_path ?? null;
  } finally {
    loading.value = false;
  }
});
</script>
