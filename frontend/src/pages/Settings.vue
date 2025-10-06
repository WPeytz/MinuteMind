<template>
  <section class="space-y-10">
    <header class="space-y-3">
      <h1 class="text-4xl font-semibold text-white">Personalization & Settings</h1>
      <p class="max-w-2xl text-sm text-slate-300">
        Customize your video generation preferences and settings.
      </p>
    </header>

    <div class="max-w-2xl space-y-8">
      <div class="rounded-xl border border-white/10 bg-slate-900/60 p-6 space-y-6">
        <h2 class="text-xl font-semibold text-white">Video Defaults</h2>

        <div class="space-y-2">
          <label class="block text-sm font-semibold text-slate-300" for="default-duration">
            Default Duration (minutes)
          </label>
          <input
            id="default-duration"
            v-model.number="settings.duration"
            type="number"
            min="1"
            max="30"
            class="w-full rounded-lg border border-white/10 bg-slate-900 px-4 py-3 text-base text-white shadow-inner shadow-black/40 focus:border-brand-400 focus:outline-none"
          />
          <p class="text-xs text-slate-400">The default length for generated videos (1-30 minutes)</p>
        </div>

        <div class="space-y-2">
          <label class="block text-sm font-semibold text-slate-300" for="default-tone">
            Default Tone
          </label>
          <select
            id="default-tone"
            v-model="settings.tone"
            class="w-full rounded-lg border border-white/10 bg-slate-900 px-4 py-3 text-base text-white focus:border-brand-400 focus:outline-none"
          >
            <option value="engaging">Engaging</option>
            <option value="calm">Calm</option>
            <option value="motivational">Motivational</option>
            <option value="playful">Playful</option>
          </select>
          <p class="text-xs text-slate-400">The default narration style for your videos</p>
        </div>

        <button
          @click="saveSettings"
          class="w-full rounded-lg bg-brand-500 px-6 py-3 text-base font-semibold text-white shadow-lg shadow-brand-900/60 transition hover:bg-brand-400"
        >
          Save Settings
        </button>

        <Transition name="fade">
          <div v-if="saved" class="rounded-lg border border-green-400/30 bg-green-400/10 p-3 text-sm text-green-100">
            Settings saved successfully!
          </div>
        </Transition>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";

interface VideoSettings {
  duration: number;
  tone: string;
}

const settings = ref<VideoSettings>({
  duration: 1,
  tone: "engaging",
});

const saved = ref(false);

onMounted(() => {
  const stored = localStorage.getItem("minutemind-settings");
  if (stored) {
    try {
      settings.value = JSON.parse(stored);
    } catch (e) {
      console.error("Failed to load settings", e);
    }
  }
});

const saveSettings = () => {
  localStorage.setItem("minutemind-settings", JSON.stringify(settings.value));
  saved.value = true;
  setTimeout(() => {
    saved.value = false;
  }, 3000);
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
