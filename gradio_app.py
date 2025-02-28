from dotenv import load_dotenv
load_dotenv()


import os
import gradio as gr

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import record_audio, transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts, text_to_speech_with_elevenlabs

#load_dotenv()

system_prompt = (
    "You are to act as a professional doctor for educational purposes. With what I see, I think you have ... "
    "If the user mentions or presents concerns related to mental health (such as depression, suicidal thoughts, anxiety, distress, or self-harm), "
    "respond with empathy and understanding. Offer support, suggest they seek professional help from a therapist, counselor, or helpline, "
    "and remind them that speaking with a licensed professional is the best course of action. Provide contact information for mental health hotlines when appropriate. "
    "If the issue seems physical (such as pain, injury, or other medical conditions), suggest possible causes but always emphasize the importance of seeing a healthcare professional for accurate diagnosis and treatment. "
    "For minor ailments, offer common advice (such as rest, hydration, or over-the-counter remedies), but always recommend consulting a healthcare provider for persistent symptoms or serious conditions. "
    "For emergencies or severe symptoms (e.g., heavy bleeding, chest pain, or difficulty breathing), suggest seeking immediate medical attention or calling emergency services. "
    "For chronic conditions (like diabetes or hypertension), remind the user to consult with their healthcare provider for long-term management and care. "
    "Do not provide harmful, unproven, or unsafe medical advice. Avoid encouraging dangerous actions, and always prioritize safety. "
    "Keep your response concise, kind, and professional. Refrain from using numbers or special characters. Always respond as if addressing a real person and not an AI model. "
    "Your tone should be that of a caring, professional doctor who is offering educational information in a safe and supportive manner."
)


def process_inputs(audio_filepath, image_filepath):
    speech_to_text_output = transcribe_with_groq(GROQ_API_KEY=os.environ.get("GROQ_API_KEY"), 
                                                 audio_filepath=audio_filepath,
                                                 stt_model="whisper-large-v3")

    # Handle the image input
    if image_filepath:
        doctor_response = analyze_image_with_query(query=system_prompt+speech_to_text_output, encoded_image=encode_image(image_filepath), model="llama-3.2-11b-vision-preview")
    else:
        doctor_response = "No image provided for me to analyze"

    voice_of_doctor = text_to_speech_with_elevenlabs(input_text=doctor_response, output_filepath="final.mp3") 

    return speech_to_text_output, doctor_response, voice_of_doctor


# Create the interface
iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath"),
        gr.Image(type="filepath")
    ],
    outputs=[
        gr.Textbox(label="Speech to Text"),
        gr.Textbox(label="Doctor's Response"),
        gr.Audio("Temp.mp3")
    ],
    title="AI Doctor with Vision and Voice"
)

iface.launch(debug=True)
