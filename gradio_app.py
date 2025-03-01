from dotenv import load_dotenv
load_dotenv()

import os
import gradio as gr
import json
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_elevenlabs
from brain_of_the_doctor import chat_with_query

hf_token = os.environ.get("HF_TOKEN")

# Load MentalBERT from Hugging Face.
mental_tokenizer = AutoTokenizer.from_pretrained("mental/mental-bert-base-uncased", token=hf_token)
mental_model = AutoModelForSequenceClassification.from_pretrained("mental/mental-bert-base-uncased", token=hf_token)

def analyze_mental_state(text):
    """
    Analyzes the text using MentalBERT and returns the distress probability.
    Assumes index 1 corresponds to "distressed" (adjust if needed).
    """
    inputs = mental_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = mental_model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    distress_prob = probs[0][1].item()  # Assumes index 1 is the "distress" class.
    return distress_prob

# Define sliding window parameters.
WINDOW_SIZE = 5
# For an average distress probability, adjust threshold based on your model's output.
DISTRESS_THRESHOLD = 0.7

def update_distress_window(window, new_score, window_size=WINDOW_SIZE):
    """
    Adds new_score to the window, ensuring it holds only the most recent window_size scores.
    Returns the updated window and the current average score.
    """
    window.append(new_score)
    if len(window) > window_size:
        window.pop(0)
    avg_score = sum(window) / len(window)
    return window, avg_score

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
    """
    Formats the conversation (state["messages"]) for display.
    """
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
    """
    Saves the conversation state to a JSON file.
    """
    with open(filename, "w") as f:
        json.dump(state, f, indent=4)

def process_inputs(audio_filepath, chat_input, conversation_state):
    """
    Processes input by:
      1. Transcribing audio (if provided) and combining with chat input.
      2. Analyzing the user's message with MentalBERT, updating a sliding window of distress scores.
      3. If the average distress exceeds the threshold, appending an alert.
      4. Appending the user's message and getting the doctor's response.
      5. Converting the doctor's response to audio.
      6. Saving and printing the conversation state.
      7. Returning the formatted conversation text, audio path, and updated state.
    """
    # Initialize conversation_state if not set.
    if not conversation_state or not isinstance(conversation_state, dict):
        conversation_state = {"messages": [SYSTEM_MESSAGE], "distress_window": []}
    
    # Validate input.
    if not audio_filepath and (not chat_input or chat_input.strip() == ""):
        conversation_text = format_conversation(conversation_state)
        print("Conversation State:\n", json.dumps(conversation_state, indent=4))
        return conversation_text, None, conversation_state

    # 1. Transcribe audio if provided.
    speech_to_text = ""
    if audio_filepath:
        speech_to_text = transcribe_with_groq(
            GROQ_API_KEY=os.environ.get("GROQ_API_KEY"),
            audio_filepath=audio_filepath,
            stt_model="whisper-large-v3"
        ).strip()
    
    # 2. Combine audio transcription and chat input.
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
        return conversation_text, None, conversation_state

    # 3. Analyze the user's message.
    distress_prob = analyze_mental_state(user_message)
    # Update the sliding window.
    window, avg_distress = update_distress_window(conversation_state.get("distress_window", []), distress_prob)
    conversation_state["distress_window"] = window
    print(f"New distress probability: {distress_prob:.2f}, Average over last {WINDOW_SIZE} messages: {avg_distress:.2f}")

    # 4. If the average distress exceeds threshold, add an alert.
    if avg_distress >= DISTRESS_THRESHOLD:
        alert_msg = "ALERT: High mental distress detected. Please consider immediate support or intervention."
        conversation_state["messages"].append({"role": "system", "content": alert_msg})
    
    # 5. Append the user's message.
    conversation_state["messages"].append({"role": "user", "content": user_message})

    # 6. Get the doctor's response.
    doctor_response = chat_with_query(
        messages=conversation_state["messages"],
        model="llama-3.2-11b-vision-preview"
    )
    conversation_state["messages"].append({"role": "assistant", "content": doctor_response})
    
    # 7. Convert the doctor's response to audio.
    audio_response_path = "final.mp3"
    text_to_speech_with_elevenlabs(
        input_text=doctor_response,
        output_filepath=audio_response_path
    )
    
    # 8. Save and print conversation state.
    save_conversation_history(conversation_state)
    print("Conversation State:\n", json.dumps(conversation_state, indent=4))
    
    # 9. Format the conversation for display.
    conversation_text = format_conversation(conversation_state)
    return conversation_text, audio_response_path, conversation_state

iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath", label="Voice Input"),
        gr.Textbox(label="Chat Input", placeholder="Type your message here..."),
        gr.State(value={})
    ],
    outputs=[
        gr.Textbox(label="Conversation", lines=10),
        gr.Audio(label="Doctor's Response (Audio)"),
        gr.State()
    ],
    title="AI Doctor Chatbot with MentalBERT Distress Score (Sliding Window)"
)

iface.launch(debug=True)









