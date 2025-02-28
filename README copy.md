# AI-Powered Voice and Vision Chatbot

This project presents an AI-driven chatbot designed to enhance patient-doctor interactions by integrating advanced speech recognition and visual analysis capabilities.

## Project Overview

The AI-Powered Voice and Vision Chatbot aims to bridge communication gaps in healthcare settings by:

- **Voice Recognition**: Utilizing OpenAI's Whisper model for accurate transcription of patient speech.
- **Visual Analysis**: Employing Meta's Llama 3.2 multimodal model to interpret medical images and provide preliminary insights.
- **Natural Responses**: Generating human-like, empathetic responses to patient inquiries.

## Features

- **Speech-to-Text (STT)**: Converts patient speech into text using Whisper.
- **Image Analysis**: Processes and analyzes medical images with Llama 3.2.
- **Text-to-Speech (TTS)**: Responds to patients with natural-sounding speech using gTTS and ElevenLabs.
- **User-Friendly Interface**: Interactive front-end developed with Gradio for real-time engagement.

## Workflow

![Workflow Diagram](https://github.com/oms0401/vision_and_voice_chatbot/blob/4cf3798784b4a5ce9ebd39a2207a8067e61891e8/workflow.png)

## Getting Started

### Prerequisites

- **Python 3.8+**: Ensure Python is installed on your system.
- **Virtual Environment**: It's recommended to use a virtual environment to manage dependencies.

### Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/oms0401/vision_and_voice_chatbot.git
   cd vision_and_voice_chatbot
   ```

2. **Set Up Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:

   Create a `.env` file in the project root directory with the following content:

   ```bash
   GROQ_API_KEY=your_groq_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   ```

5. **Install FFmpeg**:

   - **Windows**: Download from [FFmpeg Official Website](https://ffmpeg.org/download.html) and add to system PATH.
   - **macOS**: Install via Homebrew: `brew install ffmpeg`.
   - **Linux**: Use the package manager: `sudo apt-get install ffmpeg`.

### Running the Application

After completing the installation steps:

```bash
python gradio_app.py
```

Open your browser and navigate to `http://localhost:7860` to interact with the chatbot.



## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **OpenAI**: For the Whisper model.
- **Meta**: For the Llama 3.2 model.
- **Gradio**: For the user interface framework.

