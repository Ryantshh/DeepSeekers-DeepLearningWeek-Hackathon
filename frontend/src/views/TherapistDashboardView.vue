<template>
    <div class="max-w-screen-xl mx-auto p-6">
      <!-- Header -->
      <div class="bg-white rounded-lg shadow-md mb-6">
        <div class="bg-blue-600 text-white p-4 rounded-t-lg">
          <h2 class="text-xl font-bold">Therapist Dashboard</h2>
        </div>
        <div class="p-4">
          <div class="flex flex-col md:flex-row md:justify-between md:items-center">
            <div>
              <h4 class="text-lg font-semibold">Patient Assessment Tools</h4>
              <p class="text-gray-600">Review Level 1 screening results and conduct Level 2 assessments for specific domains.</p>
            </div>
            <div class="mt-4 md:mt-0 flex flex-wrap gap-2">
              <button @click="showInstructions" class="px-4 py-2 border border-blue-500 text-blue-500 rounded hover:bg-blue-50 transition-colors">
                View Instructions
              </button>
              <button @click="loadAssessmentFiles" class="px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors">
                Refresh Files
              </button>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Instructions Modal -->
      <div v-if="instructionsModalVisible" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div class="flex justify-between items-center p-4 border-b">
            <h5 class="text-lg font-semibold">Therapist Dashboard Instructions</h5>
            <button @click="instructionsModalVisible = false" class="text-gray-500 hover:text-gray-700">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="p-4">
            <h5 class="font-semibold mb-2">Using the Dashboard</h5>
            <ol class="list-decimal pl-5 mb-4 space-y-2">
              <li><strong>Select a Level 1 Assessment:</strong> Click on any file in the "Level 1 Assessment Results" section to view the patient's initial screening results.</li>
              <li><strong>Review Domain Scores:</strong> The dashboard will display all domains with their risk percentages and severity levels.</li>
              <li><strong>Select a Domain for Level 2 Assessment:</strong> Click on any domain card or use the dropdown menu to select a specific domain for deeper assessment.</li>
              <li><strong>Select a Therapy Session:</strong> Choose a therapy session text file to analyze.</li>
              <li><strong>Run the Assessment:</strong> Click the "Run Assessment" button to analyze the therapy session text using the appropriate Level 2 assessment tool.</li>
              <li><strong>Review Results:</strong> The system will display detailed results of the Level 2 assessment, including scores, interpretation, and evidence from the text.</li>
            </ol>
            
            <h5 class="font-semibold mb-2">About the Assessment Tools</h5>
            <p class="mb-2">This dashboard uses validated clinical assessment tools for each domain:</p>
            <ul class="list-disc pl-5 mb-4 space-y-1">
              <li><strong>Depression:</strong> PHQ-9 (Patient Health Questionnaire-9)</li>
              <li><strong>Anxiety:</strong> GAD-7 (Generalized Anxiety Disorder-7)</li>
              <li><strong>Suicidal Ideation:</strong> C-SSRS (Columbia-Suicide Severity Rating Scale)</li>
              <li><strong>Substance Use:</strong> ASSIST (Alcohol, Smoking and Substance Involvement Screening Test)</li>
            </ul>
            
            <div class="bg-blue-50 p-3 rounded border border-blue-200">
              <strong>Note:</strong> This tool is designed to assist clinical judgment, not replace it. All assessments should be interpreted within the context of your professional clinical evaluation.
            </div>
          </div>
          <div class="p-4 border-t flex justify-end">
            <button @click="instructionsModalVisible = false" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors">
              Got it
            </button>
          </div>
        </div>
      </div>
  
      <!-- File Selection -->
      <div class="bg-white rounded-lg shadow-md mb-6">
        <div class="p-4 border-b">
          <h5 class="font-semibold">Level 1 Assessment Results</h5>
        </div>
        <div class="p-4">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="md:col-span-2">
              <div class="border rounded p-2 max-h-56 overflow-y-auto flex flex-wrap gap-2" id="assessmentFileList">
                <div v-if="loadingFiles" class="w-full flex flex-col items-center justify-center py-4">
                  <div class="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
                  <p class="mt-2">Loading files...</p>
                </div>
                <div v-else-if="assessmentFiles.length === 0" class="w-full flex items-center justify-center py-4">
                  <p class="text-gray-500">No assessment files found</p>
                </div>
                <div 
                  v-else
                  v-for="file in assessmentFiles" 
                  :key="file" 
                  @click="selectFile(file)"
                  :class="['p-3 border rounded cursor-pointer hover:bg-gray-50 transition-colors flex-grow basis-1/2 max-w-[calc(50%-0.5rem)]', 
                    selectedFile === file ? 'border-blue-500 bg-blue-50' : 'border-gray-200']"
                >
                  <div class="flex items-center">
                    <span class="truncate">{{ formatFileName(file) }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div>
              <div class="bg-blue-50 p-3 rounded border border-blue-200 mb-3">
                <h6 class="font-semibold mb-1">Instructions</h6>
                <p class="text-sm">Select a Level 1 assessment file to view domain analysis</p>
              </div>
              <div v-if="selectedFile" class="border rounded p-3">
                <h6 class="font-semibold mb-1">Patient Information</h6>
                <p class="text-sm">Assessment from {{ formatFileDate(selectedFile) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Domain Selection -->
      <div class="bg-white rounded-lg shadow-md mb-6">
        <div class="p-4 border-b flex justify-between items-center">
          <h5 class="font-semibold">Domain Overview</h5>
        </div>
        <div class="p-4">
          <div class="mb-4">
            <label for="domainSelect" class="block text-sm font-medium mb-2">Assessment Toolkits</label>
            <select 
              v-model="selectedDomain" 
              @change="onDomainSelectChange"
              class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              id="domainSelect"
            >
              <option value="">Select a domain for Level 2 assessment</option>
              <optgroup v-if="highRiskDomains.length > 0" label="High Risk Domains">
                <option v-for="domain in highRiskDomains" :key="domain.name" :value="domain.name">
                  {{ domain.name }} ({{ domain.risk_percentage }}%)
                </option>
              </optgroup>
              <optgroup v-if="otherDomains.length > 0" label="Other Domains">
                <option v-for="domain in otherDomains" :key="domain.name" :value="domain.name">
                  {{ domain.name }} ({{ domain.risk_percentage }}%)
                </option>
              </optgroup>
            </select>
          </div>
  
          <div v-if="!fileSelected" class="text-center py-5">
            <p class="text-gray-500">Select a Level 1 assessment file to view domains</p>
          </div>
          <div v-else-if="loadingDomainData" class="text-center py-5">
            <div class="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
            <p class="mt-2">Loading domain data...</p>
          </div>
          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div 
              v-for="domain in domainData" 
              :key="domain.name" 
              @click="selectDomain(domain.name)"
              :class="['bg-white border rounded-lg shadow-sm overflow-hidden cursor-pointer transition transform hover:-translate-y-1 hover:shadow-md', 
                selectedDomain === domain.name ? 'border-blue-500 shadow-md' : '',
                domain.clinical_concern && domain.severity !== 'Mild' && domain.risk_percentage > 25 ? 'border-l-4 border-l-red-500' : '']"
            >
              <div class="flex justify-between items-center p-3 bg-gray-50 border-b">
                <h6 class="font-semibold text-sm">{{ domain.name }}</h6>
                <span 
                  class="px-2 py-1 text-xs font-semibold rounded text-white"
                  :style="{ backgroundColor: domain.severity_color || getSeverityColor(domain.severity) }"
                >{{ domain.severity }}</span>
              </div>
              <div class="p-4">
                <div class="flex items-center">
                  <div class="relative w-20 h-20 mr-4">
                    <canvas :id="`chart-${domain.name.replace(/\s+/g, '-')}`" class="w-full h-full"></canvas>
                    <div class="absolute inset-0 flex items-center justify-center font-bold">
                      {{ domain.risk_percentage }}%
                    </div>
                  </div>
                  <div>
                    <p class="text-sm mb-1">Total Score: {{ domain.total }}</p>
                    <p class="text-xs text-gray-500">Click to select for Level 2 assessment</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Level 2 Assessment -->
      <div class="bg-white rounded-lg shadow-md mb-6">
        <div class="p-4 border-b">
          <h5 class="font-semibold">Level 2 Assessment</h5>
        </div>
        <div class="p-4">
          <div v-if="!selectedDomain" class="text-center py-5">
            <p class="text-gray-500">Select a domain to perform a Level 2 assessment</p>
          </div>
  
          <!-- Assessment Form -->
          <div v-else-if="!showAssessmentResults" class="space-y-6">
            <h5 class="font-semibold">{{ selectedDomain }} Assessment</h5>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <div class="mb-4">
                  <label for="sessionSelect" class="block text-sm font-medium mb-2">Select Therapy Session</label>
                  <select 
                    v-model="selectedSession" 
                    @change="onSessionSelectChange"
                    class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    id="sessionSelect"
                  >
                    <option value="">Select a therapy session</option>
                    <option v-for="session in therapySessions" :key="session" :value="session">
                      {{ formatSessionName(session) }}
                    </option>
                  </select>
                </div>
  
                <div v-if="sessionPreview" class="border rounded p-4 bg-gray-50 max-h-48 overflow-y-auto">
                  <p class="font-medium mb-2">Preview:</p>
                  <p class="text-sm text-gray-700">{{ sessionPreview }}...</p>
                </div>
              </div>
              
              <div>
                <div v-if="currentTool" class="bg-blue-50 p-4 rounded border border-blue-200 mb-4">
                  <h6 class="font-semibold mb-1">{{ currentTool.name }}</h6>
                  <p class="text-sm mb-3">{{ currentTool.description }}</p>
                  <p class="text-xs">This assessment contains {{ currentTool.questions.length }} questions. Select a therapy session to begin.</p>
                </div>
                
                <div class="mt-4">
                  <button 
                    @click="runAssessment" 
                    :disabled="!selectedSession || assessmentLoading"
                    class="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:bg-blue-300 disabled:cursor-not-allowed"
                  >
                    <span v-if="assessmentLoading">
                      <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing...
                    </span>
                    <span v-else>Run Assessment</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
  
          <!-- Assessment Results -->
          <div v-else-if="showAssessmentResults" class="space-y-6">
            <div class="flex justify-between items-center">
              <h5 class="font-semibold">{{ selectedDomain }} Assessment Results</h5>
              <button 
                @click="showAssessmentResults = false"
                class="px-3 py-1 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 text-sm"
              >
                Back to Assessment
              </button>
            </div>
            
            <div 
              class="p-4 rounded" 
              :style="{ borderLeft: `5px solid ${currentSeverity.color}`, backgroundColor: `${currentSeverity.color}10` }"
            >
              <h6 class="font-semibold">Assessment Summary: {{ currentTool?.name }}</h6>
              <p class="mb-1">Total Score: <strong>{{ assessmentTotalScore }}/{{ currentTool?.maxScore }}</strong></p>
              <p class="mb-1">Interpretation: <strong>{{ currentSeverity.level }}</strong></p>
              <p class="mb-1">Based on analysis of therapy session: {{ formatSessionName(selectedSession) }}</p>
            </div>
  
            <div>
              <div class="flex justify-between mb-1">
                <span>Score: {{ assessmentTotalScore }}/{{ currentTool?.maxScore }}</span>
                <span>{{ Math.round((assessmentTotalScore / (currentTool?.maxScore || 1)) * 100) }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-3">
                <div 
                  class="h-3 rounded-full" 
                  :style="{ width: `${Math.round((assessmentTotalScore / (currentTool?.maxScore || 1)) * 100)}%`, backgroundColor: currentSeverity.color }"
                ></div>
              </div>
            </div>
  
            <div class="space-y-4">
              <div 
                v-for="(question, index) in currentTool?.questions" 
                :key="index"
                class="p-4 rounded"
                :style="{ borderLeft: `3px solid ${getScoreColor(assessmentResult.scores[index])}` }"
              >
                <div class="flex justify-between items-center mb-2">
                  <div class="font-medium">
                    <strong>Q{{ index + 1 }}:</strong> {{ question }}
                  </div>
                  <div>
                    <span 
                      class="px-2 py-1 text-xs font-medium rounded"
                      :style="{ backgroundColor: `${getScoreColor(assessmentResult.scores[index])}10`, 
                        color: getScoreColor(assessmentResult.scores[index]), 
                        border: `1px solid ${getScoreColor(assessmentResult.scores[index])}` }"
                    >
                      Score: {{ assessmentResult.scores[index] }}
                    </span>
                  </div>
                </div>
                <div class="mt-2 p-3 bg-gray-50 rounded text-sm italic text-gray-600">
                  {{ assessmentResult.evidence[index] || 'No specific evidence found.' }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import Chart from 'chart.js/auto';
  
  export default {
    name: 'TherapistDashboardView',
    data() {
      return {
        // UI state
        instructionsModalVisible: false,
        loadingFiles: true,
        loadingDomainData: false,
        fileSelected: false,
        assessmentLoading: false,
        showAssessmentResults: false,
        
        // Data
        assessmentFiles: [],
        selectedFile: null,
        domainData: [],
        selectedDomain: '',
        therapySessions: [],
        selectedSession: '',
        sessionPreview: '',
        assessmentResult: { scores: [], evidence: [] },
        
        // Charts
        domainCharts: {},
        
        // Assessment tools definitions
        assessmentTools: {
          "Depression": {
            name: "PHQ-9 (Patient Health Questionnaire-9)",
            description: "A 9-item depression scale to assist clinicians with diagnosing depression and monitoring treatment response.",
            maxScore: 27,
            questions: [
              "Little interest or pleasure in doing things",
              "Feeling down, depressed, or hopeless",
              "Trouble falling/staying asleep, sleeping too much",
              "Feeling tired or having little energy",
              "Poor appetite or overeating",
              "Feeling bad about yourself or that you're a failure or have let yourself or your family down",
              "Trouble concentrating on things, such as reading the newspaper or watching television",
              "Moving or speaking so slowly that other people could have noticed, or the opposite—being so fidgety or restless",
              "Thoughts that you would be better off dead or of hurting yourself in some way"
            ],
            interpretation: [
              { range: [0, 4], level: "None to minimal depression", color: "#28a745" },
              { range: [5, 9], level: "Mild depression", color: "#17a2b8" },
              { range: [10, 14], level: "Moderate depression", color: "#ffc107" },
              { range: [15, 19], level: "Moderately severe depression", color: "#fd7e14" },
              { range: [20, 27], level: "Severe depression", color: "#dc3545" }
            ]
          },
          "Anxiety": {
            name: "GAD-7 (Generalized Anxiety Disorder-7)",
            description: "A 7-item anxiety scale to screen for and measure the severity of generalized anxiety disorder.",
            maxScore: 21,
            questions: [
              "Feeling nervous, anxious, or on edge",
              "Not being able to stop or control worrying",
              "Worrying too much about different things",
              "Trouble relaxing",
              "Being so restless that it's hard to sit still",
              "Becoming easily annoyed or irritable",
              "Feeling afraid as if something awful might happen"
            ],
            interpretation: [
              { range: [0, 4], level: "Minimal anxiety", color: "#28a745" },
              { range: [5, 9], level: "Mild anxiety", color: "#17a2b8" },
              { range: [10, 14], level: "Moderate anxiety", color: "#ffc107" },
              { range: [15, 21], level: "Severe anxiety", color: "#dc3545" }
            ]
          },
          "Suicidal Ideation": {
            name: "C-SSRS (Columbia-Suicide Severity Rating Scale)",
            description: "A tool that helps identify whether someone is at risk for suicide.",
            maxScore: 25,
            questions: [
              "Have you wished you were dead or wished you could go to sleep and not wake up?",
              "Have you actually had any thoughts about killing yourself?",
              "Have you thought about how you might kill yourself?",
              "Have you had any intention of acting on these thoughts?",
              "Have you made a plan for a suicide attempt?"
            ],
            interpretation: [
              { range: [0, 5], level: "Low risk", color: "#28a745" },
              { range: [6, 15], level: "Moderate risk", color: "#ffc107" },
              { range: [16, 25], level: "High risk", color: "#dc3545" }
            ]
          },
          // More tools can be added for other domains
        }
      };
    },
    computed: {
      highRiskDomains() {
        return this.domainData.filter(d => d.risk_percentage >= 50);
      },
      otherDomains() {
        return this.domainData.filter(d => d.risk_percentage < 50);
      },
      currentTool() {
        return this.selectedDomain ? this.assessmentTools[this.selectedDomain] : null;
      },
      assessmentTotalScore() {
        return this.assessmentResult.scores.reduce((sum, score) => sum + score, 0);
      },
      currentSeverity() {
        if (!this.currentTool) return { level: "Unknown", color: "#6c757d" };
        
        const score = this.assessmentTotalScore;
        
        // Find the matching interpretation level
        for (const level of this.currentTool.interpretation) {
          if (score >= level.range[0] && score <= level.range[1]) {
            return level;
          }
        }
        
        // If no matching level found (shouldn't happen with proper data)
        return { 
          level: "Unknown", 
          color: "#6c757d",
          description: "Score outside expected range" 
        };
      }
    },
    mounted() {
      this.loadAssessmentFiles();
    },
    methods: {
      // UI Methods
      showInstructions() {
        this.instructionsModalVisible = true;
      },
      
      // Data Loading Methods
      async loadAssessmentFiles() {
        this.loadingFiles = true;
        try {
          const response = await axios.get('http://127.0.0.1:5001/api/assessment-files');
          this.assessmentFiles = response.data.files || [];
        } catch (error) {
          console.error('Error loading assessment files:', error);
          this.assessmentFiles = [];
        } finally {
          this.loadingFiles = false;
        }
      },
      
      async loadTherapySessions() {
        try {
          const response = await axios.get('http://127.0.0.1:5001/api/therapy-sessions');
          this.therapySessions = response.data.files || [];
        } catch (error) {
          console.error('Error loading therapy sessions:', error);
          this.therapySessions = [];
        }
      },
      
      async loadFileData(file) {
        this.loadingDomainData = true;
        try {
          const response = await axios.get(`http://127.0.0.1:5001/api/assessment-data?file=${file}`);
          this.domainData = response.data.domains || [];
          this.fileSelected = true;
          
          // Clear any existing charts
          this.destroyCharts();
          
          // Wait for DOM to update before creating charts
          this.$nextTick(() => {
            this.createDomainCharts();
          });
        } catch (error) {
          console.error('Error loading file data:', error);
          this.domainData = [];
        } finally {
          this.loadingDomainData = false;
        }
      },
      
      async loadSessionPreview(session) {
        if (!session) {
          this.sessionPreview = '';
          return;
        }
        
        try {
          const response = await axios.get(`http://127.0.0.1:5001/api/therapy-session?file=${session}`);
          if (response.data.content) {
            // Show just a preview (first 200 characters)
            this.sessionPreview = response.data.content.substring(0, 200);
          } else {
            this.sessionPreview = '';
          }
        } catch (error) {
          console.error('Error loading session preview:', error);
          this.sessionPreview = '';
        }
      },
      
      async runAssessment() {
        if (!this.selectedDomain || !this.selectedSession) {
          return;
        }
        
        this.assessmentLoading = true;
        try {
          const response = await axios.post('http://127.0.0.1:5001/api/run-assessment', {
            domain: this.selectedDomain,
            session: this.selectedSession,
            tool: this.currentTool?.name
          });
          
          this.assessmentResult = response.data;
          this.showAssessmentResults = true;
        } catch (error) {
          console.error('Error running assessment:', error);
          // You could show an error message here
        } finally {
          this.assessmentLoading = false;
        }
      },
      
      // Chart Methods
      createDomainCharts() {
        this.domainData.forEach(domain => {
          const canvasId = `chart-${domain.name.replace(/\s+/g, '-')}`;
          const canvas = document.getElementById(canvasId);
          
          if (canvas) {
            const ctx = canvas.getContext('2d');
            const severityColor = domain.severity_color || this.getSeverityColor(domain.severity);
            
            const chart = new Chart(ctx, {
              type: 'doughnut',
              data: {
                datasets: [{
                  data: [domain.risk_percentage, 100 - domain.risk_percentage],
                  backgroundColor: [severityColor, '#f2f2f2'],
                  borderWidth: 0
                }]
              },
              options: {
                cutout: '70%',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { display: false },
                  tooltip: { enabled: false }
                }
              }
            });
            
            this.domainCharts[canvasId] = chart;
          }
        });
      },
      
      destroyCharts() {
        Object.values(this.domainCharts).forEach(chart => {
          chart.destroy();
        });
        this.domainCharts = {};
      },
      
      // Event Handlers
      selectFile(file) {
        this.selectedFile = file;
        this.loadFileData(file);
        
        // Reset domain selection
        this.selectedDomain = '';
        this.showAssessmentResults = false;
      },
      
      selectDomain(domainName) {
        this.selectedDomain = domainName;
        this.showAssessmentResults = false;
        
        // Load therapy sessions
        this.loadTherapySessions();
      },
      
      onDomainSelectChange() {
        if (this.selectedDomain) {
          this.selectDomain(this.selectedDomain);
        }
      },
      
      onSessionSelectChange() {
        this.loadSessionPreview(this.selectedSession);
      },
      
      // Helper Functions
      formatFileName(file) {
        const dateMatch = file.match(/\d{8}_\d{6}/);
        if (dateMatch) {
          const dateStr = dateMatch[0];
          const year = dateStr.substring(0, 4);
          const month = dateStr.substring(4, 6);
          const day = dateStr.substring(6, 8);
          const hour = dateStr.substring(9, 11);
          const minute = dateStr.substring(11, 13);
          
          const date = new Date(year, month-1, day, hour, minute);
          return `Assessment - ${date.toLocaleDateString()} ${date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
        }
        return file;
      },
      
      formatFileDate(file) {
        const dateMatch = file.match(/\d{8}/);
        if (dateMatch) {
          const dateStr = dateMatch[0];
          const year = dateStr.substring(0, 4);
          const month = dateStr.substring(4, 6);
          const day = dateStr.substring(6, 8);
          
          return new Date(year, month-1, day).toLocaleDateString();
        }
        return 'Unknown date';
      },
      
      formatSessionName(session) {
        const dateMatch = session.match(/\d{8}/);
        if (dateMatch) {
          const dateStr = dateMatch[0];
          const year = dateStr.substring(0, 4);
          const month = dateStr.substring(4, 6);
          const day = dateStr.substring(6, 8);
          
          const date = new Date(year, month-1, day);
          return `Session - ${date.toLocaleDateString()}`;
        }
        return session;
      },
      
      getSeverityColor(severity) {
        switch (severity) {
          case "None": return "#28a745"; // Green
          case "Slight/Rare": return "#17a2b8"; // Teal
          case "Mild": return "#ffc107"; // Yellow
          case "Moderate": return "#fd7e14"; // Orange
          case "Severe": return "#dc3545"; // Red
          default: return "#6c757d"; // Gray
        }
      },
      
      getScoreColor(score) {
        if (score === 0) return '#6c757d'; // Gray
        if (score === 1) return '#17a2b8'; // Teal
        if (score === 2) return '#ffc107'; // Yellow
        if (score === 3) return '#fd7e14'; // Orange
        return '#dc3545'; // Red
      }
    }
  };
  </script>