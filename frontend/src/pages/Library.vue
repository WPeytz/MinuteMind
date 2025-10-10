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
        <button
          @click="handleDelete(video.video_id)"
          :disabled="deleting === video.video_id"
          class="inline-flex items-center gap-2 rounded-lg border border-red-400/30 bg-red-400/10 px-3 py-2 text-sm text-red-300 transition hover:border-red-400/60 hover:bg-red-400/20 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <span v-if="deleting === video.video_id">Deleting...</span>
          <span v-else>🗑 Delete</span>
        </button>
      </VideoCard>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import { fetchVideos, deleteVideo } from "@/api/client";
import type { VideoMetadata } from "@/api/types";
import VideoCard from "@/components/VideoCard.vue";

const loading = ref(true);
const videos = ref<VideoMetadata[]>([]);
const deleting = ref<string | null>(null);

onMounted(async () => {
  try {
    videos.value = await fetchVideos();
  } finally {
    loading.value = false;
  }
});

const handleDelete = async (videoId: string) => {
  if (!confirm("Are you sure you want to delete this video? This action cannot be undone.")) {
    return;
  }

  deleting.value = videoId;
  try {
    await deleteVideo(videoId);
    // Remove from local list
    videos.value = videos.value.filter((v) => v.video_id !== videoId);
  } catch (error) {
    alert("Failed to delete video. Please try again.");
    console.error("Delete error:", error);
  } finally {
    deleting.value = null;
  }
};
</script>
