<template>
  <main>
    <RouterView />
  </main>
</template>

<script setup lang="ts">
import { RouterView } from "vue-router";
</script>

<style scoped>
main {
  margin: 2rem auto;
  max-width: 720px;
  padding: 0 1rem;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
</style>
