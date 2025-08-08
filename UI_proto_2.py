# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 15:47:39 2025

@author: barat
"""

import tkinter as tk
from tkinter import scrolledtext
import threading
import json
import time
import llm_v2
import Text_to_Speech
from stt_handler_v2 import StreamingSTT

class VoiceAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Assistant Prototype")

        self.status_label = tk.Label(root, text="Status: Idle (Say 'Hey' or 'Start' to start)", font=("Arial", 12))
        self.status_label.pack(pady=5)

        self.log_widget = scrolledtext.ScrolledText(root, state='disabled', width=70, height=20, font=("Arial", 10))
        self.log_widget.pack(padx=10, pady=10)

        self.mode = "idle"  # idle or active
        self.chat_history = []

        # STT config path
        self.stt_config_path = r"D:\NSUB\Prototype\config.json"
        self.stt = StreamingSTT(self.stt_config_path)

        # Start listening thread
        self.listening_thread = threading.Thread(target=self.listen_loop, daemon=True)
        self.listening_thread.start()

    def log_text(self, message):
        self.log_widget.config(state='normal')
        self.log_widget.insert(tk.END, message)
        self.log_widget.see(tk.END)
        self.log_widget.config(state='disabled')

    def listen_loop(self):
        while True:
            try:
                stt_start = time.time()
                self.log_text("Listening...\n")
                stt_result = self.stt.stream_transcribe(max_seconds=30)
                stt_end = time.time()

                if stt_result["success"] and stt_result["text"]:
                    text = stt_result["text"].lower().strip()
                    self.log_text(f"you said: {text}\n")

                    if self.mode == "idle":
                        if "hey" in text or "start" in text:
                            self.mode = "active"
                            self.status_label.config(text="Status: Active (Ask your questions and say 'goodbye' or 'stop' to stop)")
                            self.log_text("Activated. You can ask your questions now.\n")
                    elif self.mode == "active":
                        if "stop" in text or "goodbye" in text:
                            self.mode = "idle"
                            self.status_label.config(text="Status: Idle (Say 'Hey assistant' to start)")
                            self.log_text("Deactivated. Say 'Hey assistant' to start again.\n")
                            self.chat_history.clear()
                        else:
                            stt_time = stt_end - stt_start
                            self.process_question(text, stt_time)
                else:
                    self.log_text("No speech detected or recognition failed.\n")

            except Exception as e:
                self.log_text(f"Error: {e}\n")

            time.sleep(0.5)

    def process_question(self, question, stt_time):
        self.log_text(f"💬 Processing: {question}\n")
        self.chat_history.append(question)

        try:
            # Start timing
            t_start = time.time()

            # LLM
            response = llm_v2.query_rag(question, self.chat_history)
            t_llm_done = time.time()

            answer = response["response"]
            self.chat_history.append(answer)
            self.log_text(f"🤖 Bot: {answer}\n")

            # Save response for TTS
            with open("LLM_response.json", "w", encoding="utf-8") as f:
                json.dump(response, f, indent=4)

            # TTS
            Text_to_Speech.main()
            t_tts_done = time.time()

            # Log processing times
            llm_time = t_llm_done - t_start
            tts_time = t_tts_done - t_llm_done
            total_time = t_tts_done - t_start

            self.log_text(f"⏱️ LLM Time: {llm_time:.2f}s\n")
            self.log_text(f"🔊 TTS Time: {tts_time:.2f}s\n")
            self.log_text(f"📊 Total Processing Time: {total_time:.2f}s\n")

        except Exception as e:
            self.log_text(f"❌ Failed to get response or TTS: {e}\n")




def main():
    root = tk.Tk()
    app = VoiceAssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
