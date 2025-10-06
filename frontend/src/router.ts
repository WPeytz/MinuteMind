import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";

import Home from "@/pages/Home.vue";
import Library from "@/pages/Library.vue";
import Player from "@/pages/Player.vue";
import Settings from "@/pages/Settings.vue";

const routes: RouteRecordRaw[] = [
  { path: "/", name: "home", component: Home },
  { path: "/library", name: "library", component: Library },
  { path: "/player/:id", name: "player", component: Player, props: true },
  { path: "/settings", name: "settings", component: Settings },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
});

export default router;
