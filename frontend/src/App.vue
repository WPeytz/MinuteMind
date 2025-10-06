<template>
  <div class="min-h-screen bg-transparent">
    <header class="border-b border-white/10 bg-slate-950/70 backdrop-blur">
      <nav class="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-4">
        <RouterLink class="text-lg font-semibold text-white" to="/">MinuteMind</RouterLink>
        <div class="flex items-center gap-4 text-sm text-slate-200">
          <RouterLink class="hover:text-brand-200" active-class="text-brand-200" to="/">Generate</RouterLink>
          <RouterLink class="hover:text-brand-200" active-class="text-brand-200" to="/library">Library</RouterLink>
          <RouterLink class="hover:text-brand-200" active-class="text-brand-200" to="/settings">Settings</RouterLink>
        </div>
      </nav>
    </header>

    <main class="mx-auto w-full max-w-6xl px-6 py-10">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
</script>
