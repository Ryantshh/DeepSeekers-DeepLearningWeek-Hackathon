<template>
  <nav class="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-custom-beige/80 border-b border-custom-beige-dark/20 shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- Logo and Navigation Links -->
        <div class="flex items-center">
          <div class="flex-shrink-0 flex items-center">
            <router-link to="/" class="text-xl font-bold text-custom-text">
              YourLogo
            </router-link>
          </div>
          <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
            <router-link 
              v-for="link in navLinks" 
              :key="link.to" 
              :to="link.to" 
              class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200"
              :class="[
                $route.path === link.to 
                  ? 'border-blue-500 text-custom-text-dark' 
                  : 'border-transparent text-custom-text hover:border-custom-beige-dark hover:text-custom-text-dark'
              ]"
            >
              {{ link.text }}
            </router-link>
          </div>
        </div>
        
        <!-- Authentication Section -->
        <div class="flex items-center">
          <!-- Not Logged In: Show Login Button -->
          <button v-if="!isAuthenticated" @click="login" class="ml-4 px-4 py-2 rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200">
            Login
          </button>
          
          <!-- Logged In: Show User Profile -->
          <div v-else class="ml-4 relative flex items-center">
            <div class="relative">
              <button @click="toggleUserMenu" class="flex items-center space-x-2 text-sm focus:outline-none">
                <img :src="user.avatar" alt="User avatar" class="h-8 w-8 rounded-full object-cover border border-custom-beige-dark">
                <span class="hidden md:block font-medium text-custom-text">{{ user.name }}</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-custom-text" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
              
              <!-- User Dropdown Menu -->
              <div v-if="userMenuOpen" class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 focus:outline-none">
                <router-link 
                  v-for="item in userMenuItems" 
                  :key="item.to" 
                  :to="item.to" 
                  class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors duration-200"
                >
                  {{ item.text }}
                </router-link>
                <button @click="logout" class="w-full text-left block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors duration-200">
                  Sign out
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Mobile menu button -->
        <div class="flex items-center sm:hidden">
          <button @click="toggleMobileMenu" class="inline-flex items-center justify-center p-2 rounded-md text-custom-text hover:text-custom-text-dark hover:bg-custom-beige-dark focus:outline-none focus:ring-2 focus:ring-inset focus:ring-custom-accent">
            <span class="sr-only">Open main menu</span>
            <svg v-if="!mobileMenuOpen" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Mobile menu -->
    <div v-if="mobileMenuOpen" class="sm:hidden bg-white">
      <div class="pt-2 pb-3 space-y-1">
        <router-link 
          v-for="link in navLinks" 
          :key="link.to" 
          :to="link.to" 
          class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium transition-colors duration-200"
          :class="[
            $route.path === link.to 
              ? 'border-blue-500 text-blue-700 bg-blue-50' 
              : 'border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800'
          ]"
        >
          {{ link.text }}
        </router-link>
      </div>
      
      <!-- Mobile authentication section -->
      <div v-if="isAuthenticated" class="pt-4 pb-3 border-t border-gray-200">
        <div class="flex items-center px-4">
          <div class="flex-shrink-0">
            <img :src="user.avatar" alt="User avatar" class="h-10 w-10 rounded-full object-cover">
          </div>
          <div class="ml-3">
            <div class="text-base font-medium text-gray-800">{{ user.name }}</div>
            <div class="text-sm font-medium text-gray-500">{{ user.email }}</div>
          </div>
        </div>
        <div class="mt-3 space-y-1">
          <router-link 
            v-for="item in userMenuItems" 
            :key="item.to" 
            :to="item.to" 
            class="block px-4 py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-100 transition-colors duration-200"
          >
            {{ item.text }}
          </router-link>
          <button @click="logout" class="w-full text-left block px-4 py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-100 transition-colors duration-200">
            Sign out
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// Navigation links
const navLinks = [
  { to: '/', text: 'Home' },
  { to: '/about', text: 'About' },
  { to: '/therapist', text: 'Therapist' },
  { to: '/transcribe', text: 'Transcribe' },
  { to: '/analysis', text: 'Mental Analysis' },
]

// User menu items
const userMenuItems = [
  { to: '/profile', text: 'Your Profile' },
  { to: '/settings', text: 'Settings' },
]

// Authentication state
const isAuthenticated = ref(false)
const user = ref({
  name: 'Jane Doe',
  email: 'jane@example.com',
  avatar: 'https://i.pravatar.cc/150?img=5'
})

// Mobile menu state
const mobileMenuOpen = ref(false)
const userMenuOpen = ref(false)

// Toggle mobile menu
const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
  if (mobileMenuOpen.value) {
    userMenuOpen.value = false
  }
}

// Toggle user dropdown menu
const toggleUserMenu = () => {
  userMenuOpen.value = !userMenuOpen.value
}

// Close dropdown when clicking outside
const closeDropdownOnClickOutside = (event) => {
  if (userMenuOpen.value && !event.target.closest('.relative')) {
    userMenuOpen.value = false
  }
}

// Login function
const login = () => {
  // Simulate login - in a real app, this would call your auth service
  isAuthenticated.value = true
  userMenuOpen.value = false
}

// Logout function
const logout = () => {
  // Simulate logout - in a real app, this would call your auth service
  isAuthenticated.value = false
  userMenuOpen.value = false
}

// Add event listener for clicks outside the dropdown
onMounted(() => {
  document.addEventListener('click', closeDropdownOnClickOutside)
})

// Clean up event listener
onUnmounted(() => {
  document.removeEventListener('click', closeDropdownOnClickOutside)
})
</script>

<style>

@layer base {
  :root {
    --color-custom-beige: 224, 218, 212;
    --color-custom-beige-dark: 200, 190, 180;
    --color-custom-text: 60, 50, 40;
    --color-custom-text-dark: 40, 30, 20;
    --color-custom-accent: 180, 160, 140;
    --color-custom-accent-dark: 160, 140, 120;
  }
}
</style>