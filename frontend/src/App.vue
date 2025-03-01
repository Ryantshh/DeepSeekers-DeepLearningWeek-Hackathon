<script setup>
import { RouterLink, RouterView } from 'vue-router'
import NavbarView from './views/NavbarView.vue'
</script>

<template>
  <div class="relative w-screen min-h-screen">
    <div class="absolute inset-0 w-full h-full bg-cover bg-center bg-[url('./assets/bg.png')] opacity-60"></div>
    
    <!-- Fixed navbar stays at the top -->
    <NavbarView class="fixed top-0 left-0 w-full z-20" />
    
    <!-- Content starts after 64px to avoid overlapping the fixed navbar -->
    <div class="relative z-10 pt-16">
      <router-view />
    </div>
  </div>
</template>

<style scoped>
/* If needed, additional styles can be added here */
</style>
