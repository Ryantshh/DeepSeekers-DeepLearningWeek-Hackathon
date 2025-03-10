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

          <!-- Static Avatar Image -->
          <div class="flex-1 relative overflow-hidden rounded-lg h-[400px]">
            <img
              :src="staticImage[gender]"
              :alt="`${gender} therapist`"
              class="w-full h-full object-cover"
            />
          </div>
        </div>

        <!-- Chat Space - Fixed height to match avatar -->
        <div class="bg-white rounded-lg shadow-md flex flex-col h-[500px]">
          <!-- Chat Header with Voice Settings -->
          <div class="p-4 border-b flex justify-between items-center">
            <h2 class="text-lg font-semibold text-gray-800">
              Chat with your AI therapist {{ gender === 'male' ? 'John' : 'Jane' }}!
            </h2>
            <div class="flex items-center space-x-2">
              <button
                @click="toggleVoiceResponse"
                class="p-2 rounded-full hover:bg-gray-100"
                :class="{ 'text-blue-500': voiceResponseEnabled }"
                title="Toggle voice responses"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                  />
                </svg>
              </button>
            </div>
          </div>

          <!-- Chat Messages -->
          <div
            class="flex-1 p-4 overflow-y-auto bg-gray-50"
            ref="messagesContainer"
            style="max-height: calc(500px - 130px)"
          >
            <div class="space-y-4">
              <div
                v-for="(message, index) in messages"
                :key="index"
                :class="[
                  'flex items-start gap-2.5',
                  message.sender === 'user' ? 'flex-row-reverse' : '',
                ]"
              >
                <div
                  :class="[
                    'w-8 h-8 rounded-full flex-shrink-0',
                    message.sender === 'user' ? 'bg-blue-200' : 'bg-gray-200',
                  ]"
                ></div>
                <div
                  :class="[
                    'rounded-lg p-3 max-w-[80%]',
                    message.sender === 'user' ? 'bg-blue-500' : 'bg-gray-200',
                  ]"
                >
                  <p
                    :class="['text-sm', message.sender === 'user' ? 'text-white' : 'text-gray-800']"
                  >
                    {{ message.text }}
                  </p>
                  <!-- Play button for AI messages -->
                  <button
                    v-if="message.sender === 'assistant'"
                    @click="speakMessage(message.text)"
                    class="mt-2 text-xs text-gray-500 hover:text-gray-700 flex items-center"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      class="h-3 w-3 mr-1"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                      />
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    Play
                  </button>
                </div>
              </div>

              <!-- Loading indicator -->
              <div v-if="isLoading" class="flex items-start gap-2.5">
                <div class="w-8 h-8 rounded-full bg-gray-200 flex-shrink-0"></div>
                <div class="bg-gray-200 rounded-lg p-3">
                  <p class="text-sm text-gray-800">
                    <span class="inline-block animate-pulse">...</span>
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Chat Input with Voice Button -->
          <div class="p-4 border-t mt-auto">
            <div class="flex items-center">
              <input
                v-model="newMessage"
                @keyup.enter="sendMessage"
                type="text"
                placeholder="Type a message..."
                class="flex-1 border rounded-l-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                :disabled="isLoading || isListening"
              />
              <button
                @click="sendMessage"
                class="bg-blue-500 text-white py-2 px-4 rounded-r-lg hover:bg-blue-600 transition-colors disabled:bg-blue-300"
                :disabled="isLoading || isListening || !newMessage.trim()"
              >
                Send
              </button>
              <button
                @click="toggleListening"
                class="bg-gray-200 text-gray-700 py-2 px-3 rounded-lg ml-2 hover:bg-gray-300 transition-colors"
                :class="{ 'bg-red-500 text-white hover:bg-red-600': isListening }"
                :disabled="isLoading"
                title="Voice input"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                  />
                </svg>
              </button>
            </div>
            <div v-if="isListening" class="mt-2 text-sm text-center text-red-500 animate-pulse">
              Listening... Say something or click the mic to stop
            </div>
          </div>
        </div>
      </div>

      <!-- Counter Button Section -->
      <div class="mt-6 text-center">
        <button
          @click="redirectToAssessment"
          :disabled="userPromptCount < requiredPrompts"
          :class="[
            'py-3 px-6 rounded-lg font-medium text-white transition-all duration-200 w-full md:w-auto',
            userPromptCount >= requiredPrompts 
              ? 'bg-green-600 hover:bg-green-700 shadow-lg hover:shadow-xl transform hover:-translate-y-1'
              : 'bg-blue-400 cursor-not-allowed'
          ]"
        >
          <span v-if="userPromptCount < requiredPrompts">
            {{ requiredPrompts - userPromptCount }} more prompts to get your mental health assessment
          </span>
          <span v-else class="flex items-center justify-center">
            Click here to get the right help!
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ml-2" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </span>
        </button>
      </div>
    </div>
  </div>
</template>
  
<script setup>
import maleNeutral from '../assets/neutral_male.png'
import femaleNeutral from '../assets/neutral_female.png'
import { ref, watch, nextTick, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// Use only the static (neutral) image for each gender
const staticImage = {
  male: maleNeutral,
  female: femaleNeutral
}

// Modified/added code for persistence
const gender = ref('female')
const newMessage = ref('')
const messages = ref([
  {
    sender: 'assistant',
    text: 'Hello! How can I help you today?',
  },
])
const isLoading = ref(false)
const messagesContainer = ref(null)
const isListening = ref(false)
const recognition = ref(null)
const voiceResponseEnabled = ref(false)
const speechSynthesis = window.speechSynthesis
let currentUtterance = null

// Prompt counter functionality
const userPromptCount = ref(0)
const requiredPrompts = 10

// Save chat state to localStorage
const saveChatState = () => {
  const chatState = {
    messages: messages.value,
    gender: gender.value,
    userPromptCount: userPromptCount.value,
    voiceResponseEnabled: voiceResponseEnabled.value
  }
  localStorage.setItem('chatState', JSON.stringify(chatState))
}

// Watch for changes in the state that should be persisted
watch([messages, gender, userPromptCount, voiceResponseEnabled], () => {
  saveChatState()
}, { deep: true })

// Computed property for conversation history
const conversationHistory = computed(() => {
  return messages.value
    .map(message => `${message.sender === 'user' ? 'Me' : 'AI'}: ${message.text}`)
    .join('\n\n')
})

// Function to redirect to mental health assessment
const redirectToAssessment = () => {
  if (userPromptCount.value >= requiredPrompts) {
    // Store conversation history in localStorage to access it from the assessment page
    localStorage.setItem('conversationHistory', conversationHistory.value)
    // Navigate to the assessment page
    router.push('/mentalhealthscreen')
  }
}

// Initialize speech recognition
const initSpeechRecognition = () => {
  if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    recognition.value = new SpeechRecognition()
    recognition.value.continuous = true
    recognition.value.interimResults = false
    recognition.value.lang = 'en-US'

    recognition.value.onresult = (event) => {
      const last = event.results.length - 1
      const transcript = event.results[last][0].transcript
      newMessage.value = transcript
    }

    recognition.value.onerror = (event) => {
      console.error('Speech recognition error', event.error)
      if (event.error !== 'no-speech') {
        isListening.value = false
      }
    }

    recognition.value.onend = () => {
      if (isListening.value) {
        try {
          recognition.value.start()
        } catch (error) {
          console.error('Failed to restart speech recognition:', error)
          isListening.value = false
        }
      }
    }
  } else {
    console.warn('Speech recognition not supported in this browser')
  }
}

const toggleListening = () => {
  if (!recognition.value) {
    initSpeechRecognition()
  }

  if (!recognition.value) {
    alert('Speech recognition is not supported in your browser.')
    return
  }

  if (isListening.value) {
    recognition.value.stop()
    isListening.value = false
    if (newMessage.value.trim()) {
      sendMessage()
    }
  } else {
    try {
      recognition.value.start()
      isListening.value = true
    } catch (error) {
      console.error('Speech recognition error:', error)
    }
  }
}

const toggleVoiceResponse = () => {
  voiceResponseEnabled.value = !voiceResponseEnabled.value
}

const speakMessage = (text) => {
  if (speechSynthesis.speaking) {
    speechSynthesis.cancel()
  }

  const utterance = new SpeechSynthesisUtterance(text)
  const voices = speechSynthesis.getVoices()
  if (voices.length > 0) {
    const englishVoices = voices.filter((voice) => voice.lang.includes('en'))
    if (englishVoices.length > 0) {
      let genderVoices = englishVoices.filter((voice) =>
        gender.value === 'female'
          ? voice.name.includes('Female') || voice.name.includes('female')
          : voice.name.includes('Male') || voice.name.includes('male')
      )
      utterance.voice = genderVoices.length > 0 ? genderVoices[0] : englishVoices[0]
    }
  }

  utterance.pitch = gender.value === 'female' ? 1.2 : 0.9
  utterance.rate = 1.0

  utterance.onstart = () => {
    // Optional: Add any start speaking actions
  }
  
  utterance.onend = () => {
    // Optional: Actions on end speaking
  }

  currentUtterance = utterance
  speechSynthesis.speak(utterance)
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const loadVoices = () => {
  return new Promise((resolve) => {
    const voices = speechSynthesis.getVoices()
    if (voices.length > 0) {
      resolve(voices)
    } else {
      speechSynthesis.onvoiceschanged = () => {
        resolve(speechSynthesis.getVoices())
      }
    }
  })
}

// Modified onMounted to restore previous chat state
onMounted(async () => {
  // Try to restore previous chat state
  const savedChatState = localStorage.getItem('chatState')
  if (savedChatState) {
    const parsedState = JSON.parse(savedChatState)
    // Restore the chat state
    messages.value = parsedState.messages
    gender.value = parsedState.gender
    userPromptCount.value = parsedState.userPromptCount
    voiceResponseEnabled.value = parsedState.voiceResponseEnabled
  }
  
  // Initialize other components
  scrollToBottom()
  initSpeechRecognition()
  await loadVoices()
})

// Add a cleanup function for component unmounting that keeps the chat state
onUnmounted(() => {
  if (speechSynthesis.speaking) {
    speechSynthesis.cancel()
  }
  if (recognition.value && isListening.value) {
    recognition.value.stop()
  }
  // Note: We're not clearing the chat state here
})

watch(
  messages,
  () => {
    scrollToBottom()
  },
  { deep: true }
)

const sendMessage = async () => {
  if (!newMessage.value.trim() || isLoading.value) return

  const userMessage = newMessage.value.trim()
  messages.value.push({
    sender: 'user',
    text: userMessage,
  })

  // Increment the prompt counter when user sends a message
  userPromptCount.value++

  newMessage.value = ''
  isLoading.value = true

  try {
    const response = await axios.post(
      'http://127.0.0.1:5000/chat',
      {
        message: userMessage
      }
    )

    const responseText = response.data["doctor_response"]

    messages.value.push({
      sender: 'assistant',
      text: responseText,
    })

    if (voiceResponseEnabled.value) {
      await nextTick()
      speakMessage(responseText)
    }
  } catch (error) {
    console.error('Error calling OpenAI API:', error)
    messages.value.push({
      sender: 'assistant',
      text: 'Sorry, I encountered an error. Please try again later.',
    })
  } finally {
    isLoading.value = false
  }
}

watch(gender, () => {
  if (speechSynthesis.speaking) {
    speechSynthesis.cancel()
  }
  const responseText = `I'm now ${gender.value === 'male' ? 'John' : 'Jane'}. How can I help you today?`
  messages.value.push({
    sender: 'assistant',
    text: responseText,
  })

  if (voiceResponseEnabled.value) {
    setTimeout(() => speakMessage(responseText), 100)
  }
})
</script>
  
<style>
/* Ensure the chat container maintains a fixed height with scrollable overflow */
.overflow-y-auto {
  overflow-y: auto;
  scrollbar-width: thin;
}
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}
.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
}
.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}
</style>