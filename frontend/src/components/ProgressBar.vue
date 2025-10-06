<template>
  <div class="h-2 w-full overflow-hidden rounded-full bg-white/10">
    <div
      class="h-full rounded-full bg-brand-500 transition-[width] duration-300"
      :style="{ width: Math.min(Math.max(percent, 0), 100) + '%' }"
    ></div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    percent?: number;
  }>(),
  { percent: 0 },
);
</script>
