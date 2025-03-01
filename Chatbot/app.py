from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import json
from brain_of_the_doctor import chat_with_query
from mood_detection import text_to_mood
from voice_of_the_doctor import text_to_speech_with_elevenlabs
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)

CORS(app)

# Load MentalBERT and CNN-BiLSTM models (same as in gradio_app.py)
hf_token = os.environ.get("HF_TOKEN")

mental_tokenizer = AutoTokenizer.from_pretrained("mental/mental-bert-base-uncased", token=hf_token)
mental_model = AutoModelForSequenceClassification.from_pretrained("mental/mental-bert-base-uncased", token=hf_token)

cnn_tokenizer = AutoTokenizer.from_pretrained("AventIQ-AI/distilbert-mental-health-prediction", token=hf_token)
cnn_model = AutoModelForSequenceClassification.from_pretrained("AventIQ-AI/distilbert-mental-health-prediction", token=hf_token)

# System message for the chatbot
SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are a professional, empathetic doctor providing concise, safe, and clear advice. "
        "Respond with empathy for mental health issues, suggest possible causes for physical ailments, "
        "and always advise consulting a qualified professional when needed. "
        "Keep your answers brief within 4-6 sentences. You are based in Singapore and part of the Institute of Mental Health in Singapore."
    )
}

# Risk analysis functions (copied from gradio_app.py)
def analyze_mental_state(text):
    inputs = mental_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = mental_model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    distress_prob = probs[0][1].item()
    return distress_prob

def analyze_suicide_tendencies(text):
    inputs = cnn_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = cnn_model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    suicide_risk = probs[0][1].item()
    return suicide_risk

def combined_risk_score(text, mental_scale=1.0, suicide_threshold=0.5, boost_value=0.8):
    critical_keywords = ["self harm", "suicide", "kill myself", "end my life", "life has no meaning"]
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in critical_keywords):
        return boost_value
    mental_score = analyze_mental_state(text) * mental_scale
    suicide_score = analyze_suicide_tendencies(text)
    if suicide_score >= suicide_threshold:
        combined = suicide_score
    else:
        combined = (mental_score + suicide_score) / 2
    return combined

WINDOW_SIZE = 5
RISK_THRESHOLD = 0.7

def update_risk_window(window, new_score, window_size=WINDOW_SIZE):
    window.append(new_score)
    if len(window) > window_size:
        window.pop(0)
    avg_score = sum(window) / len(window)
    return window, avg_score

def process_mood_report(report_str):
    lines = report_str.strip().splitlines()
    if len(lines) < 2:
        return "Invalid mood report format"
    header = lines[0]
    data_line = lines[1]
    header_fields = header.split(",")
    data_fields = data_line.split(",")
    emotions = header_fields[2:]
    try:
        scores = [float(x) for x in data_fields[2:]]
    except ValueError:
        return "Error parsing mood scores"
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:3]
    top_emotions = []
    for idx in top_indices:
        emotion = emotions[idx]
        percentage = scores[idx] * 100
        top_emotions.append(f"{emotion}: {percentage:.2f}%")
    return ", ".join(top_emotions)

# Conversation state management (in-memory for simplicity; consider a database for production)
conversation_states = {}

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_id = data.get('user_id', 'default')  # Unique identifier for each user session
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Initialize conversation state if not exists
    if user_id not in conversation_states:
        conversation_states[user_id] = {"messages": [SYSTEM_MESSAGE], "risk_window": []}
    
    state = conversation_states[user_id]

    # Mood analysis
    mood_report_raw = text_to_mood(user_message)
    processed_mood = process_mood_report(mood_report_raw)
    state["messages"].append({"role": "system", "content": f"Mood Report: {processed_mood}"})

    # Risk assessment
    risk_score = combined_risk_score(user_message)
    window, avg_risk = update_risk_window(state["risk_window"], risk_score)
    state["risk_window"] = window

    if avg_risk >= RISK_THRESHOLD:
        alert_msg = "CRITICAL ALERT: High suicide risk detected. Immediate intervention is recommended."
        state["messages"].append({"role": "system", "content": alert_msg})

    # Add user message
    state["messages"].append({"role": "user", "content": user_message})

    # Get doctor response
    doctor_response = chat_with_query(
        messages=state["messages"],
        model="llama-3.2-11b-vision-preview"
    )
    state["messages"].append({"role": "assistant", "content": doctor_response})

    # Generate audio response (optional, can be toggled based on frontend needs)
    # audio_response_path = "final.mp3"
    # text_to_speech_with_elevenlabs(
    #     input_text=doctor_response,
    #     output_filepath=audio_response_path
    # )

    # Update conversation state
    conversation_states[user_id] = state

    # Prepare response
    response = {
        'doctor_response': doctor_response,
        'mood_report': processed_mood,
        'risk_score': risk_score,
        'avg_risk': avg_risk,
    }
    # 'audio_path': audio_response_path if os.path.exists(audio_response_path) else None

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)