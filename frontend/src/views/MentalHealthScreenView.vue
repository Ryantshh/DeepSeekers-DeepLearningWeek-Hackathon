<template>
  <div class="max-w-screen-xl mx-auto p-4">
    <!-- Assessment Form (shown before analysis) -->
    <div v-if="!analysisCompleted" class="bg-white rounded-lg p-8 shadow mb-8">
      <h1 class="text-center text-2xl font-bold mb-4">Your Mental Health Check-In</h1>
      <form @submit.prevent="analyzeText">
        <div class="mb-4">
          <label class="block text-gray-700 mb-2">
            Share your thoughts or feelings below to identify potential mental health concerns:
          </label>
          <textarea
            v-model="text"
            rows="8"
            placeholder="Enter your journal entries, thoughts, or any text that describes how you've been feeling lately..."
            class="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring focus:border-blue-300"
          ></textarea>
        </div>
        <div>
          <button
            type="submit"
            class="w-full bg-blue-600 text-white rounded-full py-3 font-medium hover:bg-blue-700 transition"
            ref="analyzeButton"
          >
            Analyze My Text
          </button>
        </div>
      </form>
      <div class="text-sm text-gray-600 italic mt-3">
        <strong>Note:</strong> This tool is for informational purposes only and does not provide
        medical advice or diagnosis. Please consult with a qualified healthcare provider regarding
        any mental health concerns.
      </div>
    </div>

    <!-- Loader -->
    <div v-if="analyzing" class="flex justify-center">
      <div
        class="w-12 h-12 border-4 border-gray-300 border-t-4 border-t-blue-500 rounded-full animate-spin"
      ></div>
    </div>

    <!-- Results Section -->
    <div v-if="analysisCompleted" class="bg-white rounded-lg p-8 shadow mt-8">
      <!-- Header Banner -->
      <div class="bg-blue-600 text-white text-center rounded-t-lg p-6 mb-6">
        <h2 class="text-xl font-bold">Your Mental Health Assessment Results</h2>
      </div>

      <!-- Analysis Summary -->
      <div class="bg-white shadow rounded-lg p-6 mb-8">
        <h3 class="text-lg font-semibold mb-3">Summary of Your Results</h3>
        <p class="mb-4">Based on your text, the following significant areas may need attention:</p>
        <div v-if="significantConcerns.length === 0" class="bg-gray-100 p-4 rounded text-center">
          <p>No significant areas of concern were identified in your text.</p>
        </div>
        <div class="bg-blue-100 text-blue-800 p-4 rounded" role="alert">
          <p class="mb-0">
            <strong>Important:</strong> This is not a clinical diagnosis. If you're experiencing
            distress or have concerns about your mental health, please consult with a healthcare
            professional.
          </p>
        </div>
      </div>

      <!-- Domain Results - Main Concerns -->
      <h3 class="text-lg font-semibold mb-3">Detailed Analysis</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <DomainCard
          v-for="(domain, index) in mainConcerns"
          :key="index"
          :domain="domain"
          :chart-id="'chart-' + index"
        />
      </div>

      <!-- Toggle for Other Domains -->
      <div
        v-if="otherDomains.length"
        class="bg-white p-4 rounded border border-gray-300 mb-8 cursor-pointer hover:bg-gray-100 text-center"
        @click="toggleOtherDomains"
      >
        <h5 class="mb-0">
          {{
            showOtherDomains
              ? '- Hide areas with lower ratings'
              : '+ View ' + otherDomains.length + ' other mental health areas with lower ratings'
          }}
        </h5>
      </div>

      <!-- Domain Results - Other Domains -->
      <div v-if="showOtherDomains" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <DomainCard
          v-for="(domain, index) in otherDomains"
          :key="index"
          :domain="domain"
          :chart-id="'other-chart-' + index"
        />
      </div>

      <div class="text-center mt-4 mb-3">
        <button
          @click="resetAssessment"
          class="w-full bg-blue-600 text-white rounded-full py-3 font-medium hover:bg-blue-700 transition"
        >
          Start a New Assessment
        </button>
      </div>
    </div>
  </div>
</template>
  
<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import axios from 'axios'
import DomainCard from './DomainCard.vue'

const text = ref('')
const analyzing = ref(false)
const analysisCompleted = ref(false)
const domains = ref([])
const showOtherDomains = ref(false)
const analyzeButton = ref(null)

// A domain is considered a significant (main) concern if:
// - clinical_concern is true,
// - severity is not "Mild", and
// - risk_percentage is greater than 25.
const mainConcerns = computed(() =>
  domains.value.filter((d) => d.clinical_concern && d.severity !== 'Mild' && d.risk_percentage > 25)
)

const otherDomains = computed(() =>
  domains.value.filter(
    (d) => !(d.clinical_concern && d.severity !== 'Mild' && d.risk_percentage > 25)
  )
)

const significantConcerns = computed(() => mainConcerns.value)

const analyzeText = async () => {
  if (!text.value.trim()) {
    alert('Please enter some text to analyze.')
    return
  }
  analyzing.value = true
  try {
    const response = await axios.post('http://127.0.0.1:5001/analyze', { text: text.value })
    domains.value = response.data.domains
    analysisCompleted.value = true
    
    // Save the analysis results to localStorage
    saveAnalysisToLocalStorage()
  } catch (error) {
    console.error('Error:', error)
    alert('An error occurred during analysis. Please try again.')
  } finally {
    analyzing.value = false
  }
}

const toggleOtherDomains = () => {
  showOtherDomains.value = !showOtherDomains.value
  
  // Save the toggle state to localStorage
  localStorage.setItem('showOtherDomains', JSON.stringify(showOtherDomains.value))
}

const resetAssessment = () => {
  text.value = ''
  analysisCompleted.value = false
  domains.value = []
  showOtherDomains.value = false
  
  // Clear the saved analysis from localStorage
  localStorage.removeItem('analysisResults')
  localStorage.removeItem('showOtherDomains')
  localStorage.removeItem('analysisCompleted')
  
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// Function to save analysis results to localStorage
const saveAnalysisToLocalStorage = () => {
  localStorage.setItem('analysisResults', JSON.stringify(domains.value))
  localStorage.setItem('analysisCompleted', JSON.stringify(analysisCompleted.value))
  localStorage.setItem('showOtherDomains', JSON.stringify(showOtherDomains.value))
}

// Load saved data from localStorage on mount
onMounted(async () => {
  // Try to load previous analysis results first
  const savedAnalysis = localStorage.getItem('analysisResults')
  const savedAnalysisCompleted = localStorage.getItem('analysisCompleted')
  const savedShowOtherDomains = localStorage.getItem('showOtherDomains')
  
  if (savedAnalysis && savedAnalysisCompleted) {
    // Restore previous analysis results
    domains.value = JSON.parse(savedAnalysis)
    analysisCompleted.value = JSON.parse(savedAnalysisCompleted)
    if (savedShowOtherDomains) {
      showOtherDomains.value = JSON.parse(savedShowOtherDomains)
    }
    
    // No need to trigger a new analysis
    return
  }
  
  // If no previous analysis, try to load conversation history and analyze
  const savedConversation = localStorage.getItem('conversationHistory')
  if (savedConversation) {
    text.value = savedConversation
    
    // Allow the DOM to update with the text value
    await nextTick()
    
    // Auto-trigger the analysis after a short delay to ensure UI is ready
    setTimeout(() => {
      if (analyzeButton.value) {
        analyzeButton.value.click()
      }
    }, 500)
  }
})
</script>