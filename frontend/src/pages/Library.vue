<template>
  <section class="mx-auto max-w-6xl space-y-8">
    <header class="space-y-2 text-center">
      <h1 class="text-3xl font-semibold text-white">Your Library</h1>
      <p class="text-sm text-slate-300">All your generated videos in one place.</p>
    </header>

    <div v-if="loading" class="rounded-lg border border-white/10 bg-slate-900/50 p-6 text-sm text-slate-200">
      Loading videos…
    </div>

    <div v-else-if="videos.length === 0" class="rounded-lg border border-white/10 bg-slate-900/50 p-6 text-sm text-slate-200">
      No videos yet. Generate a script on the home page to get started.
    </div>

    <div v-else class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
      <VideoCard v-for="video in videos" :key="video.video_id" :video="video">
        <RouterLink
          :to="{ name: 'player', params: { id: video.video_id }, query: { src: video.storage_path ?? '' } }"
          class="inline-flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-sm text-brand-100 hover:border-brand-400/60 hover:text-brand-200"
        >
          ▶︎ Open Player
        </RouterLink>
      </VideoCard>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import { fetchVideos } from "@/api/client";
import type { VideoMetadata } from "@/api/types";
import VideoCard from "@/components/VideoCard.vue";

const loading = ref(true);
const videos = ref<VideoMetadata[]>([]);

onMounted(async () => {
  try {
    videos.value = await fetchVideos();
  } finally {
    loading.value = false;
  }
});
</script>
