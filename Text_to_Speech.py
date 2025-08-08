import os
import json
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()

def create_speech_config():
    """Create and configure speech synthesis settings"""
    speech_config = speechsdk.SpeechConfig(
        subscription=os.environ.get('SPEECH_KEY'), 
        endpoint=os.environ.get('ENDPOINT')
    )
    speech_config.speech_synthesis_voice_name = 'en-US-AvaMultilingualNeural'
    return speech_config

def create_audio_config():
    """Create audio output configuration"""
    return speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

def get_text_input(json_file_path, json_key="response"):
    """Get text from JSON file
    
    Args:
        json_file_path (str): Path to JSON file
        json_key (str): Key to extract from JSON file. Defaults to "response".
    
    Returns:
        str: Text to be synthesized
    """
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data[json_key]

def synthesize_speech(text, speech_synthesizer):
    """Synthesize speech from text and handle results"""
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and endpoint values?")

def main():
    """Main function to orchestrate the text-to-speech process"""
    load_environment()
    
    speech_config = create_speech_config()
    audio_config = create_audio_config()
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, 
        audio_config=audio_config
    )
    
    # Specify your JSON file path
    json_file_path = r"D:\NSUB\Prototype\LLM_response.json"  # Change to your JSON file path
    text = get_text_input(json_file_path)
    synthesize_speech(text, speech_synthesizer)

if __name__ == "__main__":
    main()