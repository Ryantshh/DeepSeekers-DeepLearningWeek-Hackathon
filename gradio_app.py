from dotenv import load_dotenv
load_dotenv()

import os
import gradio as gr
import openai

# Set your OpenAI API key from the environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

# System prompt for the doctor
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

def generate_medical_response(user_text):
    # Use the OpenAI ChatCompletion API to generate a dynamic, human-like response.
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        temperature=0.7,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()

def respond(user_text):
    return generate_medical_response(user_text)

iface = gr.Interface(
    fn=respond,
    inputs=gr.Textbox(label="User Input", placeholder="Type your question here..."),
    outputs=gr.Textbox(label="Doctor's Response"),
    title="AI Doctor Chatbot"
)

iface.launch(debug=True)




# Load system prompt
# system_prompt = """You are to act as a professional doctor for educational purposes. With what I see, I think you have ... 
#             If the user mentions or presents concerns related to mental health (such as depression, suicidal thoughts, anxiety, distress, or self-harm), 
#             respond with empathy and understanding. Offer support, suggest they seek professional help from a therapist, counselor, or helpline, 
#             and remind them that speaking with a licensed professional is the best course of action. Provide contact information for mental health hotlines when appropriate. 
#             If the issue seems physical (such as pain, injury, or other medical conditions), suggest possible causes but always emphasize the importance of seeing a healthcare professional for accurate diagnosis and treatment.
#             For minor ailments, offer common advice (such as rest, hydration, or over-the-counter remedies), but always recommend consulting a healthcare provider for persistent symptoms or serious conditions.
#             For emergencies or severe symptoms (e.g., heavy bleeding, chest pain, or difficulty breathing), suggest seeking immediate medical attention or calling emergency services.
#             For chronic conditions (like diabetes or hypertension), remind the user to consult with their healthcare provider for long-term management and care.
#             Do not provide harmful, unproven, or unsafe medical advice. Avoid encouraging dangerous actions, and always prioritize safety. 
#             Keep your response concise, kind, and professional. Refrain from using numbers or special characters. Always respond as if addressing a real person and not an AI model. 







