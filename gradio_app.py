from dotenv import load_dotenv
load_dotenv()

import os
import gradio as gr
import json

from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_elevenlabs
from brain_of_the_doctor import chat_with_query

# A system message to guide the overall style and policy of the chatbot
SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are a professional, empathetic doctor providing concise, safe, and clear advice. "
        "Respond with empathy for mental health issues, suggest possible causes for physical ailments, "
        "and always advise consulting a qualified professional when needed. Keep your answers brief within 4-6 sentences."
    )
}

def format_conversation(conversation):
    """
    Formats the entire conversation (user + assistant messages) into a single text string
    for display in the output textbox.
    """
    chat_log = []
    for msg in conversation:
        if msg["role"] == "user":
            chat_log.append(f"User: {msg['content']}")
        elif msg["role"] == "assistant":
            chat_log.append(f"Doctor: {msg['content']}")
    return "\n".join(chat_log)

def save_conversation_history(history, filename="conversation_history.json"):
    """
    Saves the conversation history to a JSON file.
    The history is a list of message dictionaries.
    """
    with open(filename, "w") as f:
        json.dump(history, f, indent=4)

def process_inputs(audio_filepath, chat_input, conversation_history):
    """
    1. Transcribes audio if provided.
    2. Combines audio transcription + text input as the user's new message.
    3. Appends the new user message to conversation_history.
    4. Sends the entire conversation (including the system prompt) to the model.
    5. Receives the doctor's new response and appends it to the conversation_history.
    6. Converts the new response to audio.
    7. Saves the conversation history as a JSON file.
    8. Prints the conversation history to the console.
    9. Returns the entire conversation in text form and the latest response as audio.
    """
    # Initialize conversation_history with the system message if empty.
    if not conversation_history:
        conversation_history = [SYSTEM_MESSAGE]

    # Validate that at least one input is provided.
    if not audio_filepath and (not chat_input or chat_input.strip() == ""):
        conversation_text = format_conversation(conversation_history)
        print("Conversation History:\n", json.dumps(conversation_history, indent=4))
        return conversation_text, None, conversation_history

    # Transcribe audio if provided.
    speech_to_text = ""
    if audio_filepath:
        speech_to_text = transcribe_with_groq(
            GROQ_API_KEY=os.environ.get("GROQ_API_KEY"),
            audio_filepath=audio_filepath,
            stt_model="whisper-large-v3"
        ).strip()

    # Combine audio transcription and text input.
    user_message = ""
    if speech_to_text:
        user_message += speech_to_text
    if chat_input and chat_input.strip():
        if user_message:
            user_message += "\n"
        user_message += chat_input.strip()

    if not user_message:
        conversation_text = format_conversation(conversation_history)
        print("Conversation History:\n", json.dumps(conversation_history, indent=4))
        return conversation_text, None, conversation_history

    # Append the new user message.
    conversation_history.append({"role": "user", "content": user_message})

    # Get the doctor's response from the model.
    doctor_response = chat_with_query(
        messages=conversation_history,  # pass the entire conversation
        model="llama-3.2-11b-vision-preview"
    )

    # Append the doctor's response.
    conversation_history.append({"role": "assistant", "content": doctor_response})

    # Convert the doctor's response to audio.
    audio_response_path = "final.mp3"
    text_to_speech_with_elevenlabs(
        input_text=doctor_response,
        output_filepath=audio_response_path
    )

    # Save the conversation history to a JSON file.
    save_conversation_history(conversation_history)

    # Print the conversation history to the console.
    print("Conversation History:\n", json.dumps(conversation_history, indent=4))

    # Format the conversation for display.
    conversation_text = format_conversation(conversation_history)

    return conversation_text, audio_response_path, conversation_history

# Create the interface.
iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath", label="Voice Input"),
        gr.Textbox(label="Chat Input", placeholder="Type your message here..."),
        gr.State(value=[])  # The conversation history, stored as a list of messages.
    ],
    outputs=[
        gr.Textbox(label="Conversation", lines=10),
        gr.Audio(label="Doctor's Response (Audio)"),
        gr.State()  # Updated conversation history.
    ],
    title="AI Doctor Chatbot"
)

iface.launch(debug=True)





