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

          <!-- Animated Avatar -->
          <AnimatedAvatar
            :gender="gender"
            :response-text="latestResponse"
            :is-speaking="isSpeaking"
          />
          <div class="p-3">
            <p class="text-gray-800 text-center font-medium capitalize">{{ gender }} Avatar</p>
          </div>
        </div>

        <!-- Chat Space -->
        <div class="bg-white rounded-lg shadow-md flex flex-col h-[500px]">
          <!-- Chat Header -->
          <div class="p-4 border-b flex justify-between items-center">
            <h2 class="text-lg font-semibold text-gray-800">
              Chat with {{ gender === 'male' ? 'John' : 'Jane' }}
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

          <!-- Chat Input -->
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
    </div>
  </div>
</template>
  
  <script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import AnimatedAvatar from '../components/AnimatedAvatar.vue'

const gender = ref('female')
const newMessage = ref('')
const messages = ref([{ sender: 'assistant', text: 'Hello! How can I help you today?' }])
const isLoading = ref(false)
const messagesContainer = ref(null)
const isListening = ref(false)
const recognition = ref(null)
const voiceResponseEnabled = ref(false)
const latestResponse = ref('')
const isSpeaking = ref(false)
const speechSynthesis = window.speechSynthesis

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
      newMessage.value = event.results[last][0].transcript
    }

    recognition.value.onerror = (event) => {
      console.error('Speech recognition error', event.error)
      if (event.error !== 'no-speech') isListening.value = false
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
  }
}

// Toggle speech recognition
const toggleListening = () => {
  if (!recognition.value) initSpeechRecognition()
  if (!recognition.value) {
    alert('Speech recognition not supported.')
    return
  }

  if (isListening.value) {
    recognition.value.stop()
    isListening.value = false
    if (newMessage.value.trim()) sendMessage()
  } else {
    recognition.value.start()
    isListening.value = true
  }
}

// Toggle voice response
const toggleVoiceResponse = () => {
  voiceResponseEnabled.value = !voiceResponseEnabled.value
}

// Speak message
const speakMessage = (text) => {
  if (speechSynthesis.speaking) speechSynthesis.cancel()

  const utterance = new SpeechSynthesisUtterance(text)
  const voices = speechSynthesis.getVoices()
  if (voices.length) {
    const englishVoices = voices.filter((v) => v.lang.includes('en'))
    if (englishVoices.length) {
      utterance.voice =
        englishVoices.find((v) =>
          gender.value === 'female'
            ? v.name.includes('Female') || v.name.includes('female')
            : v.name.includes('Male') || v.name.includes('male')
        ) || englishVoices[0]
    }
  }
  utterance.pitch = gender.value === 'female' ? 1.2 : 0.9
  utterance.rate = 1.0

  isSpeaking.value = true
  utterance.onend = () => (isSpeaking.value = false)
  speechSynthesis.speak(utterance)
}

// Scroll to bottom
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// Load voices
const loadVoices = () => {
  return new Promise((resolve) => {
    const voices = speechSynthesis.getVoices()
    if (voices.length) resolve(voices)
    else speechSynthesis.onvoiceschanged = () => resolve(speechSynthesis.getVoices())
  })
}

onMounted(async () => {
  scrollToBottom()
  initSpeechRecognition()
  await loadVoices()
})

onUnmounted(() => {
  if (speechSynthesis.speaking) speechSynthesis.cancel()
  if (recognition.value && isListening.value) recognition.value.stop()
})

watch(messages, scrollToBottom, { deep: true })

// Send message to OpenAI
const sendMessage = async () => {
  if (!newMessage.value.trim() || isLoading.value) return

  const userMessage = newMessage.value.trim()
  messages.value.push({ sender: 'user', text: userMessage })
  newMessage.value = ''
  isLoading.value = true

  try {
    const response = await axios.post(
      'https://api.openai.com/v1/chat/completions',
      {
        model: 'gpt-4o-mini',
        messages: [
          {
            role: 'system',
            content: `You are a helpful and caring therapist named ${
              gender.value === 'male' ? 'John' : 'Jane'
            }. Keep responses conversational and friendly and reply to negative statements with positive affirmations.`,
          },
          ...messages.value.map((msg) => ({
            role: msg.sender === 'user' ? 'user' : 'assistant',
            content: msg.text,
          })),
        ],
        max_tokens: 1000,
      },
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${import.meta.env.VITE_OPENAI_API_KEY}`,
        },
      }
    )

    const responseText = response.data.choices[0].message.content
    messages.value.push({ sender: 'assistant', text: responseText })
    latestResponse.value = responseText

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
  if (speechSynthesis.speaking) speechSynthesis.cancel()
  const responseText = `I'm now ${
    gender.value === 'male' ? 'John' : 'Jane'
  }. How can I help you today?`
  messages.value.push({ sender: 'assistant', text: responseText })
  latestResponse.value = responseText
  if (voiceResponseEnabled.value) setTimeout(() => speakMessage(responseText), 100)
})
</script>
  
  <style>
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