<template>
  <div class="max-w-6xl mx-auto p-6">
    <h1 class="text-3xl font-bold mb-8">Audio Transcription</h1>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Left Column: Inputs -->
      <div class="bg-white shadow-md rounded-lg p-6 space-y-6">
        <div>
          <label class="block text-sm font-medium mb-2">Upload Audio File</label>
          <div class="flex items-center justify-center w-full">
            <label
              for="dropzone-file"
              class="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100"
            >
              <div class="flex flex-col items-center justify-center pt-5 pb-6">
                <svg
                  class="w-10 h-10 mb-3 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  ></path>
                </svg>
                <p class="mb-2 text-sm text-gray-500">
                  <span class="font-semibold">Click to upload</span> or drag and drop
                </p>
                <p class="text-xs text-gray-500">MP3, WAV, or M4A (MAX. 800MB)</p>
              </div>
              <input
                id="dropzone-file"
                type="file"
                class="hidden"
                accept="audio/*"
                @change="handleFileUpload"
              />
            </label>
          </div>
          <p v-if="file" class="mt-2 text-sm text-gray-600">Selected file: {{ file.name }}</p>
        </div>

        <div class="space-y-2">
          <label class="block text-sm font-medium">Model Size</label>
          <select v-model="form.model_size" class="w-full p-2 border rounded">
            <option v-for="size in modelSizes" :key="size" :value="size">{{ size }}</option>
          </select>
        </div>

        <div class="space-y-2">
          <label class="block text-sm font-medium">Chunk Length (minutes)</label>
          <input
            type="range"
            v-model.number="form.chunk_minutes"
            min="1"
            max="60"
            step="1"
            class="w-full"
          />
          <span>{{ form.chunk_minutes }}</span>
        </div>

        <div class="space-y-2">
          <label class="block text-sm font-medium">Language</label>
          <select v-model="form.language" class="w-full p-2 border rounded">
            <option v-for="lang in languages" :key="lang" :value="lang">{{ lang }}</option>
          </select>
        </div>

        <button
          @click="transcribe"
          :disabled="!file || loading"
          class="w-full bg-blue-600 text-white p-3 rounded-lg text-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 transition duration-300"
        >
          {{ loading ? 'Transcribing...' : 'Transcribe Audio' }}
        </button>
      </div>

      <!-- Right Column: Outputs -->
      <div class="bg-white shadow-md rounded-lg p-6 space-y-6">
        <div>
          <label class="block text-sm font-medium mb-2">Transcription</label>
          <div
            v-if="result.transcript"
            class="p-4 border rounded bg-gray-50 h-96 overflow-auto"
            v-html="formattedTranscript"
          ></div>
          <div
            v-else
            class="p-4 border rounded bg-gray-50 h-96 flex items-center justify-center text-gray-500"
          >
            No transcription yet
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium mb-2">Status</label>
          <div class="p-3 border rounded bg-gray-50">
            {{ result.status || 'Awaiting transcription...' }}
          </div>
        </div>

        <div v-if="result.output_file">
          <a
            :href="downloadUrl"
            target="_blank"
            class="inline-block bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition duration-300"
          >
            Download Transcript
          </a>
        </div>
      </div>
    </div>
  </div>
</template>
  
  <script>
export default {
  data() {
    return {
      file: null,
      loading: false,
      form: {
        model_size: 'base',
        chunk_minutes: 30,
        language: 'en',
      },
      result: {
        transcript: '',
        output_file: '',
        status: '',
      },
      modelSizes: ['tiny', 'base', 'small', 'medium', 'large', 'large-v2'],
      languages: ['auto', 'en', 'fr', 'de', 'es', 'it', 'ja', 'zh', 'ru'],
    }
  },
  computed: {
    formattedTranscript() {
      return this.result.transcript
        .replace(/\n/g, '<br>')
        .replace(/## (.*)/g, '<h2 class="text-xl font-semibold mt-4 mb-2">$1</h2>')
    },
    downloadUrl() {
      return `http://localhost:8000/download/${this.result.output_file.split('/').pop()}`
    },
  },
  methods: {
    handleFileUpload(event) {
      this.file = event.target.files[0]
    },
    async transcribe() {
      if (!this.file) return

      this.loading = true
      const formData = new FormData()
      formData.append('audio_file', this.file)
      Object.keys(this.form).forEach((key) => formData.append(key, this.form[key]))

      try {
        const response = await fetch('http://localhost:8000/transcribe/', {
          method: 'POST',
          body: formData,
        })
        const data = await response.json()
        if (response.ok) {
          this.result = data
        } else {
          this.result.status = data.detail
        }
      } catch (error) {
        this.result.status = `Error: ${error.message}`
      } finally {
        this.loading = false
      }
    },
  },
}
</script>
  
  <style scoped>
/* Add any component-specific styles here */
</style>