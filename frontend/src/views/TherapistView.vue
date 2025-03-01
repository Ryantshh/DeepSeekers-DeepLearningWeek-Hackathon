<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8 text-custom-text-dark">Find a Therapist</h1>

    <!-- Search and Filter Bar -->
    <div class="mb-8 flex flex-col sm:flex-row gap-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search therapists..."
        class="flex-grow p-2 border border-custom-beige-dark rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <select
        v-model="selectedSpecialization"
        class="p-2 border border-custom-beige-dark rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">All Specializations</option>
        <option v-for="spec in specializations" :key="spec" :value="spec">
          {{ spec }}
        </option>
      </select>
    </div>

    <!-- Therapist Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="therapist in filteredTherapists"
        :key="therapist.name"
        class="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300"
      >
        <div class="flex items-center mb-4">
          <img
            :src="getImageUrl(therapist.imageUrl)"
            :alt="therapist.name"
            class="w-16 h-16 rounded-full object-cover mr-4"
          />
          <div>
            <h2 class="text-xl font-semibold text-custom-text-dark">{{ therapist.name }}</h2>
            <p class="text-sm text-custom-text">{{ therapist.specialise }}</p>
          </div>
        </div>
        <p class="text-custom-text italic">"{{ therapist.quote }}"</p>
      </div>
    </div>
  </div>
</template>
  
  <script setup>
import { ref, computed, onMounted } from 'vue'
import therapistsData from '@/data/therapist.json'

const therapists = ref([])
const searchQuery = ref('')
const selectedSpecialization = ref('')
const specializations = ref([])

function getImageUrl(name) {
  // note that this does not include files in subdirectories
  return new URL(name, import.meta.url).href
}

onMounted(() => {
  therapists.value = therapistsData
  specializations.value = [...new Set(therapists.value.flatMap((t) => t.specialise.split(', ')))]
})

const filteredTherapists = computed(() => {
  return therapists.value.filter((therapist) => {
    const nameMatch = therapist.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    const specMatch =
      selectedSpecialization.value === '' ||
      therapist.specialise.includes(selectedSpecialization.value)
    return nameMatch && specMatch
  })
})
</script>
  
  <style scoped>
/* Add any component-specific styles here */
</style>