from dotenv import load_dotenv
load_dotenv()


import os
from gtts import gTTS

import subprocess
import platform



#Step1b: Setup Text to Speech–TTS–model with ElevenLabs
import elevenlabs
from elevenlabs.client import ElevenLabs

ELEVENLABS_API_KEY=os.environ.get("ELEVENLABS_API_KEY")

from pydub import AudioSegment

def change_audio_speed(input_filepath, output_filepath, speed=1.25):
    """
    Changes the playback speed of an audio file.
    
    Args:
        input_filepath (str): Path to the original audio file.
        output_filepath (str): Path to save the modified audio file.
        speed (float): Factor by which to speed up the audio. (e.g., 1.25 for 25% faster)
    """
    audio = AudioSegment.from_file(input_filepath)
    # Modify the frame rate
    new_frame_rate = int(audio.frame_rate * speed)
    fast_audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_frame_rate})
    # Export the audio with the original frame rate so that playback is faster
    fast_audio = fast_audio.set_frame_rate(audio.frame_rate)
    fast_audio.export(output_filepath, format="mp3")
    
# Example usage:
change_audio_speed("final.mp3", "final_fast.mp3", speed=1.25)


def text_to_speech_with_gtts(input_text, output_filepath):
    language="en"

    audioobj= gTTS(
        text=input_text,
        lang=language,
        slow=False
    )
    audioobj.save(output_filepath)
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(['afplay', output_filepath])
        elif os_name == "Windows":
            from pydub import AudioSegment
            wav_filepath = output_filepath.replace(".mp3", ".wav")
            AudioSegment.from_mp3(output_filepath).export(wav_filepath, format="wav")
            subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{wav_filepath}").PlaySync();'])  
            
        elif os_name == "Linux":  # Linux
            subprocess.run(['aplay', output_filepath])  # Alternative: use 'mpg123' or 'ffplay'
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"An error occurred while trying to play the audio: {e}")


input_text="Hi this is Ai with Hassan, autoplay testing!"
#text_to_speech_with_gtts(input_text=input_text, output_filepath="gtts_testing_autoplay.mp3")


def text_to_speech_with_elevenlabs(input_text, output_filepath):
    client=ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio=client.generate(
        text= input_text,
        voice= "Charlotte",
        output_format= "mp3_22050_32",
        model= "eleven_turbo_v2"
    )
    elevenlabs.save(audio, output_filepath)
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(['afplay', output_filepath])
        elif os_name == "Windows":
             from pydub import AudioSegment
             wav_filepath = output_filepath.replace(".mp3", ".wav")
             AudioSegment.from_mp3(output_filepath).export(wav_filepath, format="wav")
             subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{wav_filepath}").PlaySync();'])
            
        elif os_name == "Linux":  # Linux
            subprocess.run(['aplay', output_filepath])  # Alternative: use 'mpg123' or 'ffplay'
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"An error occurred while trying to play the audio: {e}")