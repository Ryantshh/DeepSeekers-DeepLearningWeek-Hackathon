from dotenv import load_dotenv
import os
import requests
import json
import time

# Load environment variables
load_dotenv()
API_KEY = os.getenv("IMENTIV_API_KEY")
BASE_URL = "https://api.imentiv.ai/v1"

HEADERS = {
    "X-API-Key": API_KEY,
    "accept": "application/json"
}

# This function takes in a text (in string) and return the mood analysis (in string as well)
def text_to_mood(aString):
    upload_url = f"{BASE_URL}/texts"

    # Ensure correct form-data format
    data = {
        "text": aString,
        "video_url": ""  # Ensures the API processes the text, not video
    }
    try:
        # Step 1: Upload the text
        response = requests.post(upload_url, headers=HEADERS, data=data)

        if response.status_code == 200:
            # Step 2: If upload is successful, retrieve the text id
            response_json = response.json()
            text_id = response_json.get("id")
            report_url = f"{BASE_URL}/texts/{text_id}/report"
            data = {
                "text_id" : text_id
            }
            # Step 3: Wait for 3 seconds before fetching the report
            time.sleep(3)
            # Step 4: Fetch the report
            report_response = requests.get(report_url, headers=HEADERS, data=data)

            if report_response.status_code == 200:
                try:
                    return report_response.text
                except ValueError as e:
                    return f"🚨 Error parsing JSON from report response: {str(e)}"
            else:
                return f"⚠️ Report API Error: {report_response.text}"
        else:
            return f"⚠️ API Error: {response.text}"

    except requests.exceptions.RequestException as e:
        return f"🚨 Request Error: {str(e)}"
    
# This function takes in an audio file and return an analysis of it (in string)
def audio_to_mood(file):
    upload_url = f"{BASE_URL}/audios"

    # Prepare the data for uploading the audio
    data = {
        "file": file,
        "video_url": ""  # Ensures the API processes the audio, not video
    }

    try:
        # Step 1: Upload the audio
        response = requests.post(upload_url, headers=HEADERS, data=data)

        if response.status_code == 200:
            # Step 2: If upload is successful, retrieve the audio id
            response_json = response.json()
            audio_id = response_json.get("id")
            report_url = f"{BASE_URL}/audio/{audio_id}/report"
            data = {
                "audio_id" :audio_id
            }
            # Step 3: Check the processing status with a while loop
            processing = True
            while processing:
                # Step 3.1: Wait for 3 seconds before checking the status
                time.sleep(3)

                # Step 3.2: Fetch the report
                report_response = requests.get(report_url, headers=HEADERS, data=data)

                if report_response.status_code == 200:
                    # If the report is available, return the report
                    try:
                        report_response = report_response.text
                        processing = False  # Exit the loop as we have the result
                        return report_response
                    except ValueError as e:
                        return f"🚨 Error parsing JSON from report response: {str(e)}"
                elif report_response.status_code == 202:
                    # If still processing, keep checking
                    print("🔄 Processing... Please wait.")
                else:
                    # If an error occurs, exit the loop and return the error
                    return f"⚠️ Report API Error: {report_response.text}"

        else:
            return f"⚠️ API Error: {response.text}"

    except requests.exceptions.RequestException as e:
        return f"🚨 Request Error: {str(e)}"

# Example usage
if __name__ == "__main__":
    sample_text = "My girlfriend broke up with me today at 3am"
    print("Text Emotion Analysis Result:")
    print(text_to_mood(sample_text))

    # sample_audio_path = "sample_audio.wav"  # Ensure this file exists
    # print("\nAudio Emotion Analysis Result:")
    # print(audio_to_mood(sample_audio_path))
