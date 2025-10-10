<template>
  <form class="space-y-6" @submit.prevent="submit">
    <div class="space-y-2">
      <label class="block text-sm font-semibold text-slate-300" for="topic">Topic</label>
      <input
        id="topic"
        v-model="topic"
        type="text"
        required
        placeholder="Enter a focus topic"
        class="w-full rounded-lg border border-white/10 bg-slate-900 px-4 py-3 text-base text-white shadow-inner shadow-black/40 focus:border-brand-400 focus:outline-none"
      />
    </div>

    <div class="flex justify-center">
      <button
        class="inline-flex items-center justify-center rounded-lg bg-brand-500 px-6 py-3 text-base font-semibold text-white shadow-lg shadow-brand-900/50 transition hover:bg-brand-400 hover:shadow-brand-800/70 disabled:cursor-not-allowed disabled:opacity-50"
        type="submit"
        :disabled="disabled"
      >
        <span v-if="busy" class="flex items-center gap-2">
          <span class="h-2 w-2 animate-ping rounded-full bg-white"></span>
          Generating…
        </span>
        <span v-else>Generate Video</span>
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from "vue";

const props = defineProps<{
  busy?: boolean;
}>();

const emit = defineEmits<{
  (e: "submit", payload: { topic: string; duration_minutes: number; tone: string }): void;
}>();

const topic = ref("");
const duration = ref(1);
const tone = ref("engaging");

const disabled = computed(() => props.busy || topic.value.trim().length === 0);

onMounted(() => {
  const stored = localStorage.getItem("minutemind-settings");
  if (stored) {
    try {
      const settings = JSON.parse(stored);
      duration.value = settings.duration || 1;
      tone.value = settings.tone || "engaging";
    } catch (e) {
      console.error("Failed to load settings", e);
    }
  }
});

const submit = () => {
  if (disabled.value) return;
  emit("submit", {
    topic: topic.value.trim(),
    duration_minutes: duration.value,
    tone: tone.value,
  });
};
</script>
