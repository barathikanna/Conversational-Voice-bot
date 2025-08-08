import json
import os
import logging
import audioop

try:
    from vosk import Model, KaldiRecognizer
except ImportError:
    raise ImportError("Please install vosk: pip install vosk")

import pyaudio

logging.basicConfig(level=logging.INFO)
    

class StreamingSTT:
    """
    Streaming Speech-to-Text handler using Vosk.
    Supports config from dict or JSON file.
    """

    def __init__(self, config):
        """
        Initialize the handler with configuration.
        Args:
            config (dict or str): Config dict or path to JSON config file.
        """
        if isinstance(config, str):
            # Load config from JSON file
            if not os.path.exists(config):
                raise FileNotFoundError(f"Config file {config} does not exist.")
            with open(config, 'r') as f:
                self.config = json.load(f)
        elif isinstance(config, dict):
            self.config = config
        else:
            raise ValueError("Config must be a dict or a JSON file path.")

        self.model_path = self.config.get("model_path")
        self.sample_rate = self.config.get("sample_rate", 16000)
        #self.silence_threshold = self.config.get("silence_threshold", 0.01)
        #self.max_silence = self.config.get("max_silence", 10.0)
        self.blocksize = self.config.get("blocksize", 1024)

        self.silence_rms_threshold = self.config.get("silence_rms_threshold", 500)
        self.max_silence_duration = self.config.get("max_silence_duration", 3.0)

        if not self.model_path or not os.path.exists(self.model_path):
            raise ValueError(f"Model path '{self.model_path}' not found.")

        logging.info(f"Loading Vosk model from: {self.model_path}")
        self.model = Model(self.model_path)

    def list_audio_devices(self):
        """
        List available audio input devices.
        Returns:
            List of device info dicts.
        """
        pa = pyaudio.PyAudio()
        devices = []
        for i in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(i)
            devices.append(info)
        pa.terminate()
        return devices

    def stream_transcribe(self, device_index=None, max_seconds=30):
        """
        Start streaming transcription from microphone.

        Args:
            device_index (int, optional): Microphone device index. If None, use default.
            max_seconds (float, optional): Max duration for a session. Defaults to 30s.

        Returns:
            dict: {
                "text": "final recognized text",
                "segments": [ {"start": float, "end": float, "text": str} ],
                "success": bool,
                "error": str or None
            }
        """
        pa = pyaudio.PyAudio()
        try:
            stream = pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.blocksize,
                input_device_index=device_index
            )
        except Exception as e:
            return {
                "text": "",
                "segments": [],
                "success": False,
                "error": f"Failed to open microphone: {e}"
            }

        rec = KaldiRecognizer(self.model, self.sample_rate)
        rec.SetWords(True)

        silent_chunks = 0
        max_silent_chunks = int(self.max_silence_duration * self.sample_rate / self.blocksize)
        speech_started = False

        frames = 0
        text = ""
        segments = []
        result = None

        logging.info("Stream started... Speak into the microphone.")

        try:
            while True:
                data = stream.read(self.blocksize, exception_on_overflow=False)

                rms = audioop.rms(data, 2)
                if rms >= self.silence_rms_threshold:
                    speech_started = True
                    silent_chunks = 0
                elif speech_started:
                    silent_chunks += 1

                if speech_started and silent_chunks > max_silent_chunks:
                    # Silence after speech detected, so we're done.
                    break

                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    seg_text = result.get("text", "")
                    text += seg_text + " "
                    # Extract word-level segments
                    if "result" in result:
                        for word in result["result"]:
                            segments.append({
                                "start": word["start"],
                                "end": word["end"],
                                "text": word["word"]
                            })
                # Stop if duration exceeds max_seconds
                frames += self.blocksize
                duration = frames / self.sample_rate
                if duration > max_seconds:
                    break
        except Exception as e:
            return {
                "text": text.strip(),
                "segments": segments,
                "success": False,
                "error": str(e)
            }
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()

        # Final partial
        final_res = json.loads(rec.FinalResult())
        final_text = final_res.get("text", "")
        text += final_text

        if "result" in final_res:
            for word in final_res["result"]:
                segments.append({
                    "start": word["start"],
                    "end": word["end"],
                    "text": word["word"]
                })

        return {
            "text": text.strip(),
            "segments": segments,
            "success": True,
            "error": None
        }