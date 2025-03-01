from dotenv import load_dotenv
load_dotenv()

import os
import gradio as gr
import json
import torch
import time
import requests
import numpy as np
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from mood_detection import text_to_mood  # your existing text_to_mood function

from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_elevenlabs
from brain_of_the_doctor import chat_with_query

hf_token = os.environ.get("HF_TOKEN")

#####################################
# Helper function to process mood report CSV
#####################################
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

#####################################
# Load MentalBERT (general distress model)
#####################################
mental_tokenizer = AutoTokenizer.from_pretrained("mental/mental-bert-base-uncased", token=hf_token)
mental_model = AutoModelForSequenceClassification.from_pretrained("mental/mental-bert-base-uncased", token=hf_token)

def analyze_mental_state(text):
    inputs = mental_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = mental_model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    distress_prob = probs[0][1].item()
    return distress_prob

#####################################
# Load CNN-BiLSTM model for suicide risk (DistilBERT-based)
#####################################
cnn_tokenizer = AutoTokenizer.from_pretrained("AventIQ-AI/distilbert-mental-health-prediction", token=hf_token)
cnn_model = AutoModelForSequenceClassification.from_pretrained("AventIQ-AI/distilbert-mental-health-prediction", token=hf_token)

def analyze_suicide_tendencies(text):
    inputs = cnn_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = cnn_model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    suicide_risk = probs[0][1].item()
    return suicide_risk

#####################################
# Combined Risk Score Calculation (with keyword boosting)
#####################################
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

#####################################
# Sliding window for recent risk scores
#####################################
WINDOW_SIZE = 5
def update_risk_window(window, new_score, window_size=WINDOW_SIZE):
    window.append(new_score)
    if len(window) > window_size:
        window.pop(0)
    avg_score = sum(window) / len(window)
    return window, avg_score

RISK_THRESHOLD = 0.7

#####################################
# Conversation Handling
#####################################
SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are a professional, empathetic doctor providing concise, safe, and clear advice. "
        "Respond with empathy for mental health issues, suggest possible causes for physical ailments, "
        "and always advise consulting a qualified professional when needed. "
        "Keep your answers brief within 4-6 sentences. You are based in Singapore and part of the Institute of Mental Health in Singapore."
    )
}

def format_conversation(state):
    chat_log = []
    for msg in state["messages"]:
        if msg["role"] == "user":
            chat_log.append(f"User: {msg['content']}")
        elif msg["role"] == "assistant":
            chat_log.append(f"Doctor: {msg['content']}")
        elif msg["role"] == "system":
            chat_log.append(f"(System): {msg['content']}")
    return "\n".join(chat_log)

def save_conversation_history(state, filename="conversation_history.json"):
    with open(filename, "w") as f:
        json.dump(state, f, indent=4)

#####################################
# Function to export all user prompts as a JSON file
#####################################
def export_user_prompts(conversation_state):
    user_prompts = [msg["content"] for msg in conversation_state.get("messages", []) if msg["role"] == "user"]
    filename = "user_prompts.json"
    with open(filename, "w") as f:
        json.dump(user_prompts, f, indent=4)
    return filename

#####################################
# Main Process Function
#####################################
def process_inputs(audio_filepath, chat_input, conversation_state):
    if not conversation_state or not isinstance(conversation_state, dict):
        conversation_state = {"messages": [SYSTEM_MESSAGE], "risk_window": []}
    
    if not audio_filepath and (not chat_input or chat_input.strip() == ""):
        conversation_text = format_conversation(conversation_state)
        print("Conversation State:\n", json.dumps(conversation_state, indent=4))
        return conversation_text, None, conversation_state, False  # False: extra button not shown

    speech_to_text = ""
    if audio_filepath:
        speech_to_text = transcribe_with_groq(
            GROQ_API_KEY=os.environ.get("GROQ_API_KEY"),
            audio_filepath=audio_filepath,
            stt_model="whisper-large-v3"
        ).strip()
    
    user_message = ""
    if speech_to_text:
        user_message += speech_to_text
    if chat_input and chat_input.strip():
        if user_message:
            user_message += "\n"
        user_message += chat_input.strip()
    
    if not user_message:
        conversation_text = format_conversation(conversation_state)
        print("Conversation State:\n", json.dumps(conversation_state, indent=4))
        return conversation_text, None, conversation_state, False

    # Run mood analysis and append mood report.
    mood_report_raw = text_to_mood(user_message)
    processed_mood = process_mood_report(mood_report_raw)
    conversation_state["messages"].append({"role": "system", "content": f"Mood Report: {processed_mood}"})
    
    # Evaluate risk score.
    risk_score = combined_risk_score(user_message)
    window, avg_risk = update_risk_window(conversation_state.get("risk_window", []), risk_score)
    conversation_state["risk_window"] = window
    print(f"New combined risk score: {risk_score:.2f}, Average over last {WINDOW_SIZE} messages: {avg_risk:.2f}")
    
    if avg_risk >= RISK_THRESHOLD:
        alert_msg = "CRITICAL ALERT: High suicide risk detected. Immediate intervention is recommended."
        conversation_state["messages"].append({"role": "system", "content": alert_msg})
    
    conversation_state["messages"].append({"role": "user", "content": user_message})
    
    doctor_response = chat_with_query(
        messages=conversation_state["messages"],
        model="llama-3.2-11b-vision-preview"
    )
    conversation_state["messages"].append({"role": "assistant", "content": doctor_response})
    
    audio_response_path = "final.mp3"
    text_to_speech_with_elevenlabs(
        input_text=doctor_response,
        output_filepath=audio_response_path
    )
    
    save_conversation_history(conversation_state)
    print("Conversation State:\n", json.dumps(conversation_state, indent=4))
    
    conversation_text = format_conversation(conversation_state)
    
    # Show extra button if there are at least 15 user messages.
    user_count = sum(1 for m in conversation_state["messages"] if m["role"] == "user")
    show_button = user_count >= 2
    
    return conversation_text, audio_response_path, conversation_state, show_button

#####################################
# Gradio Interface using Blocks for dynamic extra button
#####################################
with gr.Blocks() as demo:
    with gr.Row():
        audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Voice Input")
        chat_input = gr.Textbox(label="Chat Input", placeholder="Type your message here...")
    state = gr.State(value={})
    submit_btn = gr.Button("Submit")
    conversation_output = gr.Textbox(label="Conversation", lines=10)
    response_audio = gr.Audio(label="Doctor's Response (Audio)")
    extra_btn = gr.Button("Get Your Diagnosis Report", visible=False)
    file_output = gr.File(label="Exported User Prompts")
    
    # Process inputs and update outputs.
    def update_all(audio_filepath, chat_input, state):
        conv_text, audio_path, new_state, show_btn = process_inputs(audio_filepath, chat_input, state)
        extra_update = gr.update(visible=show_btn)
        return conv_text, audio_path, new_state, extra_update

    submit_btn.click(
        update_all,
        inputs=[audio_input, chat_input, state],
        outputs=[conversation_output, response_audio, state, extra_btn]
    )
    
    # When extra button is clicked, export user prompts.
    def export_prompts(state):
        filename = export_user_prompts(state)
        return filename

    extra_btn.click(
        export_prompts,
        inputs=[state],
        outputs=[file_output]
    )
    
demo.launch(debug=True)

















