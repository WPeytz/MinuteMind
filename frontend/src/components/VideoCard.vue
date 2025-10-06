<template>
  <article class="rounded-xl border border-white/10 bg-slate-900/60 p-5 shadow-lg shadow-black/40">
    <header class="mb-4 flex items-start justify-between gap-3">
      <div>
        <h3 class="text-lg font-semibold text-white">{{ video.title }}</h3>
        <p class="text-xs uppercase tracking-wide text-slate-400">{{ formattedDate }}</p>
      </div>
      <span
        class="rounded-full px-3 py-1 text-xs font-semibold"
        :class="video.status === 'completed' ? 'bg-green-500/20 text-green-300' : 'bg-yellow-500/20 text-yellow-200'"
      >
        {{ video.status }}
      </span>
    </header>
    <p class="text-sm text-slate-300">ID: {{ video.video_id }}</p>
    <div class="mt-4 flex flex-wrap items-center gap-3">
      <slot />
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from "vue";

import type { VideoMetadata } from "@/api/types";

const props = defineProps<{
  video: VideoMetadata;
}>();

const formattedDate = computed(() => new Date(props.video.created_at).toLocaleString());
</script>
