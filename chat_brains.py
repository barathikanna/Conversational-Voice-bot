import llm_v2
import traceback
import json
import Text_to_Speech
from stt_handler_v2 import StreamingSTT

#my_question = "what can you tell me about the ocean?"
#chat_history = ["what do you know about the beaches?"]

def main():                 

    my_question = ""
    chat_history = []

    # --- 1. Listen for the Question (STT Part) ---
    #stt_config_path = "config.json"
    stt_config_path = r"D:\NSUB\Prototype\config.json"
    stt = StreamingSTT(stt_config_path)

        
    while True:
        print("Listening for your question... (Speak for up to 30 seconds)")
        stt_result = stt.stream_transcribe(max_seconds=30)

        if stt_result["success"] and stt_result["text"]:
            my_question = stt_result["text"]
            print(f"\nRecognized Question: \"{my_question}\"")

        try:
            response = llm_v2.query_rag(my_question, chat_history)
            print("\n--- Process finished successfully in main.py ---")

            json_output = json.dumps(response, indent=4)
            output_filename = "LLM_response.json"

            with open(output_filename, "w") as f:
                f.write(json_output)

            chat_history.append(my_question)
            chat_history.append(response['response'])
            print("Response ready for TTS")
            #print(chat_history)

            try:
                Text_to_Speech.main()
            except Exception as e:
                traceback.print_exc()
        except Exception as e:
            traceback.print_exc()

if __name__ == "__main__":          
    main()