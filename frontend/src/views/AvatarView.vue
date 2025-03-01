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

          <!-- Animated Avatar with Expressions -->
          <div class="flex-1 relative overflow-hidden rounded-lg">
            <!-- Male Avatar with expressions -->
            <div v-if="gender === 'male'" class="h-[400px] relative">
              <img
                v-for="expression in expressions"
                :key="expression"
                :src="expressionImages[gender][expression]"
                :alt="`Male ${expression} expression`"
                class="w-full h-full object-cover absolute top-0 left-0 transition-opacity duration-300"
                :class="currentExpression === expression ? 'opacity-100' : 'opacity-0'"
              />
              <!-- Fallback if images aren't available -->
              <!-- <div 
                v-if="!expressionImagesLoaded" 
                class="absolute inset-0 flex items-center justify-center bg-gray-200"
              >
                <div class="text-center">
                  <div class="w-32 h-32 mx-auto rounded-full bg-gray-300 flex items-center justify-center mb-4">
                    <div class="flex flex-col items-center">
                      
                      <div class="flex space-x-4 mb-2">
                        <div class="w-3 h-3 bg-gray-700 rounded-full"></div>
                        <div class="w-3 h-3 bg-gray-700 rounded-full"></div>
                      </div>
                      
                      <div 
                        class="w-10 h-2 bg-gray-700 rounded-full transform transition-all duration-300"
                        :class="{
                          'scale-y-1': currentExpression === 'neutral',
                          'scale-y-[-1]': currentExpression === 'happy',
                          'scale-y-2': currentExpression === 'sad',
                          'scale-x-150': currentExpression === 'surprised'
                        }"
                      ></div>
                    </div>
                  </div>
                  <p class="text-gray-700 font-medium capitalize">{{ currentExpression }} Expression</p>
                </div>
              </div> -->
            </div>
            
            <!-- Female Avatar with expressions -->
            <div v-else class="h-[400px] relative">
              <img
                v-for="expression in expressions"
                :key="expression"
                :src="expressionImages[gender][expression]"
                :alt="`Female ${expression} expression`"
                class="w-full h-full object-cover absolute top-0 left-0 transition-opacity duration-300"
                :class="currentExpression === expression ? 'opacity-100' : 'opacity-0'"
              />
              <!-- Fallback if images aren't available -->
              <!-- <div 
                v-if="!expressionImagesLoaded" 
                class="absolute inset-0 flex items-center justify-center bg-gray-200"
              >
                <div class="text-center">
                  <div class="w-32 h-32 mx-auto rounded-full bg-gray-300 flex items-center justify-center mb-4">
                    <div class="flex flex-col items-center">
                      
                      <div class="flex space-x-4 mb-2">
                        <div class="w-3 h-3 bg-gray-700 rounded-full"></div>
                        <div class="w-3 h-3 bg-gray-700 rounded-full"></div>
                      </div>
                      
                      <div 
                        class="w-10 h-2 bg-gray-700 rounded-full transform transition-all duration-300"
                        :class="{
                          'scale-y-1': currentExpression === 'neutral',
                          'scale-y-[-1]': currentExpression === 'happy',
                          'scale-y-2': currentExpression === 'sad',
                          'scale-x-150': currentExpression === 'surprised'
                        }"
                      ></div>
                    </div>
                  </div>
                  <p class="text-gray-700 font-medium capitalize">{{ currentExpression }} Expression</p>
                </div>
              </div> -->
            </div>
            
            <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/50 to-transparent p-3">
              <p class="text-white text-center font-medium capitalize">
                {{ gender }} Therapist - {{ currentExpression }}
              </p>
            </div>
          </div>
        </div>

        <!-- Chat Space - Fixed height to match avatar -->
        <div class="bg-white rounded-lg shadow-md flex flex-col h-[500px]">
          <!-- Chat Header with Voice Settings -->
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

          <!-- Chat Messages - Fixed height with overflow -->
          <div
            class="flex-1 p-4 overflow-y-auto bg-gray-50"
            ref="messagesContainer"
            style="max-height: calc(500px - 130px)"
          >
            <div class="space-y-4">
              <!-- Actual Messages -->
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
            <!-- Voice recognition status -->
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
import maleNeutral from '../assets/neutral_male.png'
import maleSad from '../assets/sad_male.png'
import maleSurprised from '../assets/surprised_male.png'
import maleEmpathetic from '../assets/empathetic_male.png'
import femaleNeutral from '../assets/neutral_female.png'
import femaleSad from '../assets/sad_female.png'
import femaleSurprised from '../assets/surprised_female.png'
import femaleEmpathetic from '../assets/empathetic_female.png'

// Create a map of your images
const expressionImages = {
  male: {
    neutral: maleNeutral,
    sad: maleSad,
    surprised: maleSurprised,
    empathetic: maleEmpathetic
  },
  female: {
    // female images
    neutral: femaleNeutral,
    sad: femaleSad,
    surprised: femaleSurprised,
    empathetic: femaleEmpathetic
  }
}

import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

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

// Expression-related variables
const expressions = ['neutral', 'happy', 'sad', 'surprised', 'empathetic', 'concerned']
const currentExpression = ref('neutral')
const expressionImagesLoaded = ref(true) // Set to false if you want to test the fallback

// Function to analyze text and determine appropriate expression
const analyzeTextForExpression = (text) => {
  text = text.toLowerCase()
  
  // Check for different emotional cues in the text
  if (text.includes('sorry') || text.includes('understand your pain') || 
      text.includes('difficult') || text.includes('challenge')) {
    return 'empathetic'
  }
  
  if (text.includes('worry') || text.includes('concerned') || 
      text.includes('serious') || text.includes('important to address')) {
    return 'concerned'
  }
  
  if (text.includes('great') || text.includes('wonderful') || 
      text.includes('happy') || text.includes('glad') || 
      text.includes('congratulations') || text.includes('proud')) {
    return 'happy'
  }
  
  if (text.includes('sad') || text.includes('unfortunate') || 
      text.includes('regret') || text.includes('disappointing')) {
    return 'sad'
  }
  
  if (text.includes('wow') || text.includes('amazing') || 
      text.includes('unexpected') || text.includes('incredible') || 
      text.includes('surprising')) {
    return 'surprised'
  }
  
  // Default to neutral for general statements
  return 'neutral'
}

// Animate expressions with transitions
const changeExpression = (newExpression) => {
  // Only change if it's different
  if (currentExpression.value !== newExpression) {
    // Animate out current expression
    currentExpression.value = newExpression
    
    // You could add more complex sequences here:
    // For example, briefly showing 'surprised' before 'happy'
    // or adding timed transitions between expressions
  }
}

// Initialize speech recognition
const initSpeechRecognition = () => {
  if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    recognition.value = new SpeechRecognition()
    recognition.value.continuous = true // Changed to true to keep listening
    recognition.value.interimResults = false
    recognition.value.lang = 'en-US'

    recognition.value.onresult = (event) => {
      const last = event.results.length - 1
      const transcript = event.results[last][0].transcript
      newMessage.value = transcript

      // Don't auto-send the message - wait for user to click send or stop
      // This fixes the premature ending
    }

    recognition.value.onerror = (event) => {
      console.error('Speech recognition error', event.error)

      // Only stop listening on actual errors, not "no-speech" which is a normal state
      if (event.error !== 'no-speech') {
        isListening.value = false
      }
    }

    recognition.value.onend = () => {
      // Don't automatically set isListening to false here
      // Only set it when user explicitly stops or when there's an error

      // If we're still supposed to be listening, restart
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

// Toggle speech recognition on/off
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

    // When manually stopping, check if we have a message to send
    if (newMessage.value.trim()) {
      sendMessage()
    }
  } else {
    try {
      recognition.value.start()
      isListening.value = true
      
      // Show surprise when user starts talking
      changeExpression('surprised')
    } catch (error) {
      console.error('Speech recognition error:', error)
    }
  }
}

// Toggle voice response setting
const toggleVoiceResponse = () => {
  voiceResponseEnabled.value = !voiceResponseEnabled.value
}

// Speak a message using text-to-speech
const speakMessage = (text) => {
  // Stop any current speech
  if (speechSynthesis.speaking) {
    speechSynthesis.cancel()
  }

  const utterance = new SpeechSynthesisUtterance(text)
  // Set voice based on gender
  const voices = speechSynthesis.getVoices()

  // Try to find appropriate voice
  if (voices.length > 0) {
    // Filter for English voices
    const englishVoices = voices.filter((voice) => voice.lang.includes('en'))

    if (englishVoices.length > 0) {
      // Try to find gender-appropriate voice
      let genderVoices = englishVoices.filter((voice) =>
        gender.value === 'female'
          ? voice.name.includes('Female') || voice.name.includes('female')
          : voice.name.includes('Male') || voice.name.includes('male')
      )

      // If no gender-specific voice found, use any English voice
      utterance.voice = genderVoices.length > 0 ? genderVoices[0] : englishVoices[0]
    }
  }

  // Adjust properties based on gender
  utterance.pitch = gender.value === 'female' ? 1.2 : 0.9
  utterance.rate = 1.0

  // Add speech synthesis events to coordinate with expressions
  utterance.onstart = () => {
    // Could show a "talking" animation here
  }
  
  utterance.onend = () => {
    // Return to neutral when done speaking
    setTimeout(() => {
      changeExpression('neutral')
    }, 1000)
  }

  currentUtterance = utterance
  speechSynthesis.speak(utterance)
}

// Function to scroll to bottom of messages
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// Load voices as soon as possible
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

// Preload avatar expression images
const preloadImages = () => {
  expressions.forEach(expression => {
    const maleImg = new Image()
    maleImg.src = `../assets/${expression}_male.png`
    
    const femaleImg = new Image()
    femaleImg.src = `../assets/${expression}_female.png`
    
    // You might want to add error handling to set expressionImagesLoaded to false
    // if the images don't exist
    maleImg.onerror = femaleImg.onerror = () => {
      expressionImagesLoaded.value = false
    }
  })
}

// Ensure scroll works on initial load and get available voices
onMounted(async () => {
  scrollToBottom()
  initSpeechRecognition()
  preloadImages()

  // Load voices
  await loadVoices()
})

// Clean up on component unmount
onUnmounted(() => {
  if (speechSynthesis.speaking) {
    speechSynthesis.cancel()
  }

  if (recognition.value && isListening.value) {
    recognition.value.stop()
  }
})

// Watch for changes in messages to scroll to bottom
watch(
  messages,
  () => {
    scrollToBottom()
  },
  { deep: true }
)

// Function to send message to OpenAI API
const sendMessage = async () => {
  if (!newMessage.value.trim() || isLoading.value) return

  // Add user message to chat
  const userMessage = newMessage.value.trim()
  messages.value.push({
    sender: 'user',
    text: userMessage,
  })

  // Show that the therapist is listening - switch to an attentive expression
  changeExpression('concerned')

  // Clear input
  newMessage.value = ''

  // Set loading state
  isLoading.value = true

  try {
    // Make API call to OpenAI
    const response = await axios.post(
      'https://api.openai.com/v1/chat/completions',
      {
        model: 'gpt-4o-mini', // or your preferred model
        messages: [
          {
            role: 'system',
            content: `You are a helpful and caring therapist named ${
              gender.value === 'male' ? 'John' : 'Jane'
            }. Keep responses conversational and friendly and reply negative statements with positive affirmations.`,
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

    // Get AI response
    const responseText = response.data.choices[0].message.content

    // Analyze text for appropriate expression
    const expressionToShow = analyzeTextForExpression(responseText)
    changeExpression(expressionToShow)

    // Add AI response to chat
    messages.value.push({
      sender: 'assistant',
      text: responseText,
    })

    // Speak the response if voice is enabled
    if (voiceResponseEnabled.value) {
      await nextTick()
      speakMessage(responseText)
    }
  } catch (error) {
    console.error('Error calling OpenAI API:', error)

    // Show concerned expression
    changeExpression('concerned')

    // Add error message
    messages.value.push({
      sender: 'assistant',
      text: 'Sorry, I encountered an error. Please try again later.',
    })
  } finally {
    isLoading.value = false
  }
}

// Update avatar response when gender changes
watch(gender, () => {
  // Stop any current speech when changing avatar
  if (speechSynthesis.speaking) {
    speechSynthesis.cancel()
  }

  const responseText = `I'm now ${
    gender.value === 'male' ? 'John' : 'Jane'
  }. How can I help you today?`

  // Reset to neutral expression first
  changeExpression('neutral')
  
  // Show happy expression for greeting
  setTimeout(() => {
    changeExpression('happy')
  }, 300)

  messages.value.push({
    sender: 'assistant',
    text: responseText,
  })

  // Speak the response if voice is enabled
  if (voiceResponseEnabled.value) {
    setTimeout(() => speakMessage(responseText), 100)
  }
})
</script>
  
<style>
/* Make sure chat container maintains fixed height with scrollable overflow */
.overflow-y-auto {
  overflow-y: auto;
  scrollbar-width: thin;
}

/* Optional styling for scrollbar */
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

/* Animation for expression transitions */
.transition-opacity {
  transition: opacity 0.3s ease-in-out;
}
</style>