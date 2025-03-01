<!-- src/components/TherapistDashboard.vue -->
<template>
  <div class="min-h-screen bg-gray-100 p-6">
    <!-- Header -->
    <header class="mb-6">
      <h1 class="text-3xl font-bold text-gray-800">Therapist Dashboard</h1>
      <p class="text-gray-600">Analyze therapy sessions and review assessment results</p>
    </header>

    <!-- Main Content -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Assessment Form -->
      <div id="assessment-form" v-show="!showResults" class="bg-white p-6 rounded-lg shadow-md">
        <h2 class="text-xl font-semibold text-gray-700 mb-4">Run Assessment</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Select Therapy Session</label>
            <select
              v-model="selectedSession"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Select a session</option>
              <option v-for="session in sessions" :key="session" :value="session">
                {{ session }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Select Domain</label>
            <select
              v-model="selectedDomain"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Select a domain</option>
              <option v-for="domain in assessmentDomains" :key="domain" :value="domain">
                {{ domain }}
              </option>
            </select>
          </div>
          <button
            @click="runAssessment"
            :disabled="!selectedSession || !selectedDomain || loading"
            class="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 disabled:bg-gray-400"
          >
            <span v-if="!loading">Run Assessment</span>
            <span v-else>Loading...</span>
          </button>
        </div>
      </div>

      <!-- Assessment Results -->
      <div id="assessment-results" v-show="showResults" class="bg-white p-6 rounded-lg shadow-md">
        <h2
          class="text-xl font-semibold text-gray-700 mb-4"
          v-text="`${selectedDomain} Assessment Results`"
        ></h2>

        <!-- Summary -->
        <div
          class="mb-6 p-4 border-l-4"
          :style="{ borderColor: severityColor, backgroundColor: `${severityColor}10` }"
        >
          <h3 class="text-lg font-medium text-gray-700">
            Assessment Summary: {{ assessmentTool?.name }}
          </h3>
          <p>
            Total Score: <strong>{{ totalScore }}/{{ assessmentTool?.maxScore }}</strong>
          </p>
          <p>
            Interpretation: <strong>{{ severityLevel }}</strong>
          </p>
          <p>Based on analysis of therapy session: {{ selectedSession }}</p>
        </div>

        <!-- Progress Bar -->
        <div class="mb-6">
          <div class="flex justify-between mb-1 text-sm">
            <span>Score: {{ totalScore }}/{{ assessmentTool?.maxScore }}</span>
            <span>{{ Math.round(scorePercentage) }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2.5">
            <div
              class="h-2.5 rounded-full"
              :style="{ width: `${scorePercentage}%`, backgroundColor: severityColor }"
            ></div>
          </div>
        </div>

        <!-- Assessment Items -->
        <div class="space-y-4">
          <div
            v-for="(question, index) in assessmentTool?.questions"
            :key="index"
            class="p-4 border-l-4"
            :style="{ borderColor: getResponseColor(results.scores[index]) }"
          >
            <div class="flex justify-between items-center mb-2">
              <div>
                <strong>Q{{ index + 1 }}:</strong> {{ question }}
              </div>
              <span
                class="px-2 py-1 rounded"
                :style="{
                  backgroundColor: `${getResponseColor(results.scores[index])}10`,
                  color: getResponseColor(results.scores[index]),
                  border: `1px solid ${getResponseColor(results.scores[index])}`,
                }"
              >
                Score: {{ results.scores[index] || 0 }}
              </span>
            </div>
            <div class="text-gray-600">
              {{ results.evidence[index] || 'No specific evidence found.' }}
            </div>
          </div>
        </div>

        <!-- Back Button -->
        <button
          @click="showResults = false"
          class="mt-4 w-full bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700"
        >
          Back to Form
        </button>
      </div>
    </div>

    <!-- Loader -->
    <div
      v-if="loading"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center"
    >
      <div class="bg-white p-4 rounded-lg shadow-lg">
        <p class="text-gray-700">Processing assessment...</p>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="mt-6 p-4 bg-red-100 border-l-4 border-red-500 text-red-700 rounded">
      <h3 class="font-semibold">Error Running Assessment</h3>
      <p>{{ error }}</p>
    </div>
  </div>
</template>
  
  <script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

// State
const sessions = ref([])
const assessmentDomains = Object.keys({
  Depression: {},
  Anxiety: {},
  'Suicidal Ideation': {},
  Anger: {},
  Mania: {},
  'Somatic Symptoms': {},
  Psychosis: {},
  'Sleep Problems': {},
  Memory: {},
  'Repetitive Thoughts and Behaviors': {},
  Dissociation: {},
  'Personality Functioning': {},
  'Substance Use': {},
})
const selectedSession = ref('')
const selectedDomain = ref('')
const loading = ref(false)
const showResults = ref(false)
const results = ref({})
const error = ref(null)

// Computed Properties
const assessmentTool = computed(() => {
  // Simulate fetching tool config (normally from backend or static import)
  const tools = {
    Depression: {
      name: 'PHQ-9',
      maxScore: 27,
      questions: ['Little interest or pleasure...', '...'],
    },
    Anxiety: { name: 'GAD-7', maxScore: 21, questions: ['Feeling nervous...', '...'] },
    // Add other tools as needed
  }
  return tools[selectedDomain.value]
})

const totalScore = computed(
  () => results.value.scores?.reduce((a, b) => a + (Number.isFinite(b) ? b : 0), 0) || 0
)
const scorePercentage = computed(
  () => (totalScore.value / (assessmentTool.value?.maxScore || 1)) * 100
)
const severityLevel = computed(() => {
  // Simplified severity calculation
  const score = totalScore.value
  if (score <= 4) return 'Minimal'
  if (score <= 9) return 'Mild'
  if (score <= 14) return 'Moderate'
  return 'Severe'
})
const severityColor = computed(() => {
  const level = severityLevel.value
  return (
    { Minimal: '#28a745', Mild: '#17a2b8', Moderate: '#ffc107', Severe: '#dc3545' }[level] ||
    '#6c757d'
  )
})

// Methods
const getResponseColor = (score) => {
  if (score === 0) return '#28a745' // Green
  if (score === 1) return '#17a2b8' // Teal
  if (score === 2) return '#ffc107' // Yellow
  if (score === 3) return '#fd7e14' // Orange
  return '#dc3545' // Red
}

const loadSessions = async () => {
  try {
    const response = await axios.get('http://localhost:5001/api/therapy-sessions')
    sessions.value = response.data.files
  } catch (err) {
    error.value = 'Failed to load therapy sessions: ' + err.message
  }
}

const runAssessment = async () => {
  if (!selectedSession.value || !selectedDomain.value) return
  loading.value = true
  error.value = null
  try {
    const response = await axios.post('http://localhost:5001/api/run-assessment', {
      domain: selectedDomain.value,
      session: selectedSession.value,
    })
    results.value = response.data
    showResults.value = true
  } catch (err) {
    error.value = err.response?.data?.error || 'An error occurred while running the assessment.'
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadSessions()
})
</script>
  
  <style scoped>
/* Add any custom styles if needed */
</style>