<script setup>
import { RouterLink, RouterView } from 'vue-router'
import NavbarView from './views/NavbarView.vue'
import AvatarView from './views/AvatarView.vue'
</script>

<template>
  <div class="relative w-screen min-h-screen">
    <div class="absolute inset-0 w-full h-full bg-cover bg-center bg-[url('./assets/bg.png')] opacity-60"></div>
    <div class="relative z-10">
      <NavbarView />
      <div>
        <AvatarView />
      </div>
      <router-view />
    </div>
  </div>
</template>

<style scoped></style>
