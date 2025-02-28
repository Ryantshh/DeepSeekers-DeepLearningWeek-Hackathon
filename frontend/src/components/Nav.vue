<template>
  <nav class="fixed top-0 w-full bg-stone-800 text-stone-100 shadow-lg z-50 transition-all duration-300"
    :class="{ 'py-4': !scrolled, 'py-2 bg-stone-800/95 backdrop-blur-sm': scrolled }">
    <div class="container mx-auto px-4 flex justify-between items-center">
      <router-link to="/" class="text-xl font-bold flex items-center space-x-2 hover:text-orange-200 transition-colors">
        <span>Chat With Me</span>
      </router-link>

      <div class="flex items-center space-x-2">
        <!-- Removed the incorrect template tag here -->
        <div class="md:flex space-x-1">
          <router-link to="/profile" class="px-4 py-2 rounded-md hover:bg-stone-700 transition-colors text-stone-100">
            Profile
          </router-link>
          <router-link to="/community"
            class="px-4 py-2 rounded-md hover:bg-stone-700 transition-colors text-stone-100">
            Community
          </router-link>
        </div>
      </div>
    </div>
  </nav>
  <!-- Spacer to prevent content from being hidden under fixed navbar -->
  <div class="h-16"></div>
</template>

<script>
import { useToast } from "vue-toastification";

export default {
  data() {
    return {
      scrolled: false,
      mobileMenuOpen: false,
      toast: useToast(),
    };
  },
  created() {
    window.addEventListener('scroll', this.handleScroll);
  },
  unmounted() {
    window.removeEventListener('scroll', this.handleScroll);
  },
  methods: {
    handleScroll() {
      this.scrolled = window.scrollY > 10;
    },
    toggleMobileMenu() {
      this.mobileMenuOpen = !this.mobileMenuOpen;
    }
  },
};
</script>
