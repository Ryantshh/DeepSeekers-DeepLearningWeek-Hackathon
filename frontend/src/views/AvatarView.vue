<template>
  <div class="min-h-screen p-4">
    <div class="max-w-6xl mx-auto">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Avatar Section -->
        <div class="bg-white rounded-lg shadow-md p-6 flex flex-col">
          <!-- Toggle Button -->
          <div class="flex justify-center mb-4">
            <div class="inline-flex items-center bg-gray-200 rounded-full p-1">
              <button
                @click="gender = 'male'"
                :class="[
                  'py-2 px-6 rounded-full transition-all duration-200',
                  gender === 'male' ? 'bg-blue-500 text-white' : 'text-gray-700',
                ]"
              >
                Male
              </button>
              <button
                @click="gender = 'female'"
                :class="[
                  'py-2 px-6 rounded-full transition-all duration-200',
                  gender === 'female' ? 'bg-pink-500 text-white' : 'text-gray-700',
                ]"
              >
                Female
              </button>
            </div>
          </div>

          <!-- Full Image Avatar -->
          <div class="flex-1 relative overflow-hidden rounded-lg">
            <img
              v-if="gender === 'male'"
              src="../assets/male.png?height=500&width=400"
              alt="Male Avatar"
              class="w-[500px] h-[500px] object-cover"
            />
            <img
              v-else
              src="../assets/female.png"
              alt="Female Avatar"
              class="w-[500px] h-[500px] object-cover"
            />
            <div
              class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/50 to-transparent p-3"
            >
              <p class="text-white text-center font-medium capitalize">{{ gender }} Avatar</p>
            </div>
          </div>
        </div>

        <!-- Chat Space -->
        <div class="bg-white rounded-lg shadow-md flex flex-col h-[500px]">
          <!-- Chat Header -->
          <div class="p-4 border-b">
            <h2 class="text-lg font-semibold text-gray-800">
              Chat with {{ gender === 'male' ? 'John' : 'Jane' }}
            </h2>
          </div>

          <!-- Chat Messages -->
          <div class="flex-1 p-4 overflow-y-auto bg-gray-50">
            <div class="space-y-4">
              <!-- Sample Messages -->
              <div class="flex items-start gap-2.5">
                <div class="w-8 h-8 rounded-full bg-gray-200 flex-shrink-0"></div>
                <div class="bg-gray-200 rounded-lg p-3 max-w-[80%]">
                  <p class="text-sm text-gray-800">Hello! How can I help you today?</p>
                </div>
              </div>

              <div class="flex items-start flex-row-reverse gap-2.5">
                <div class="w-8 h-8 rounded-full bg-blue-200 flex-shrink-0"></div>
                <div class="bg-blue-500 rounded-lg p-3 max-w-[80%]">
                  <p class="text-sm text-white">I'd like to know more about my avatar options.</p>
                </div>
              </div>

              <div class="flex items-start gap-2.5">
                <div class="w-8 h-8 rounded-full bg-gray-200 flex-shrink-0"></div>
                <div class="bg-gray-200 rounded-lg p-3 max-w-[80%]">
                  <p class="text-sm text-gray-800">
                    You can customize your {{ gender }} avatar with different outfits and
                    accessories.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Chat Input -->
          <div class="p-4 border-t">
            <div class="flex items-center">
              <input
                type="text"
                placeholder="Type a message..."
                class="flex-1 border rounded-l-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                class="bg-blue-500 text-white py-2 px-4 rounded-r-lg hover:bg-blue-600 transition-colors"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
  
  <script setup>
import { ref } from 'vue'

const gender = ref('female')
</script>
  
  <style>
/* Additional styles can be added here if needed */
</style>