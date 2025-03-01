<template>
  <div :class="['bg-white rounded-lg shadow overflow-hidden', clinicalClass]">
    <!-- Card Header -->
    <div class="bg-gray-100 p-4 flex justify-between items-center">
      <h5 class="mb-0 font-semibold">{{ domain.name }}</h5>
      <span
        class="px-2 py-1 text-xs font-semibold rounded text-white"
        :style="{ backgroundColor: domain.severity_color }"
      >
        {{ domain.severity }}
      </span>
    </div>

    <!-- Card Body -->
    <div class="p-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Chart Section -->
        <div>
          <div class="relative h-40 w-40 mx-auto">
            <canvas :id="chartId" ref="chartCanvas"></canvas>
            <div
              class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-xl font-bold"
            >
              {{ domain.risk_percentage }}%
            </div>
          </div>
        </div>

        <!-- Questions & Evidence -->
        <div>
          <h6 class="mb-3 font-semibold">Question Scores</h6>
          <div>
            <div v-for="(question, qIndex) in domain.questions" :key="qIndex" class="mb-4">
              <div class="flex items-center text-sm mb-1">
                <span
                  class="inline-block w-6 h-6 flex items-center justify-center rounded-full text-white text-xs mr-2"
                  :style="{ backgroundColor: scoreColor(getScore(qIndex)) }"
                >
                  {{ getScore(qIndex) }}
                </span>
                <span>{{ question }}</span>
              </div>
              <div
                v-if="getScore(qIndex) > 0"
                class="mt-2 p-2 bg-gray-100 rounded italic text-sm text-gray-600"
              >
                {{ domain.evidence[qIndex] || 'No evidence provided for this question.' }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
  
  <script setup>
import { onMounted, ref, computed } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  domain: {
    type: Object,
    required: true,
  },
  chartId: {
    type: String,
    required: true,
  },
})

const chartCanvas = ref(null)

// If the domain is a clinical concern, add a red left border.
const clinicalClass = computed(() =>
  props.domain.clinical_concern ? 'border-l-4 border-red-500' : ''
)

const getScore = (index) => {
  return props.domain.scores && props.domain.scores[index] !== undefined
    ? props.domain.scores[index]
    : 0
}

const scoreColor = (score) => {
  if (score === 0) return '#6c757d'
  if (score === 1) return '#17a2b8'
  if (score === 2) return '#ffc107'
  if (score === 3) return '#fd7e14'
  return '#dc3545'
}

const createChart = () => {
  const ctx = chartCanvas.value.getContext('2d')
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [
        {
          data: [props.domain.risk_percentage, 100 - props.domain.risk_percentage],
          backgroundColor: [props.domain.domain_color, '#f2f2f2'],
          borderWidth: 0,
        },
      ],
    },
    options: {
      cutout: '70%',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false },
      },
    },
  })
}

onMounted(() => {
  createChart()
})
</script>
  