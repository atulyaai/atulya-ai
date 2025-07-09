"""
Atulya AI - Voice Interface (v0.1.0)
Full STT and TTS implementation with Whisper and Coqui
"""

import os
import logging
import tempfile
import wave
import time
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import io

# Configure logging
logger = logging.getLogger(__name__)

class VoiceInterface:
    """Full voice interface with STT and TTS capabilities"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.stt_model = None
        self.tts_model = None
        self.audio_config = {
            "sample_rate": int(os.getenv("AUDIO_SAMPLE_RATE", "16000")),
            "channels": int(os.getenv("AUDIO_CHANNELS", "1")),
            "format": os.getenv("AUDIO_FORMAT", "wav")
        }
        
        # Initialize models
        self._init_stt()
        self._init_tts()
    
    def _init_stt(self):
        """Initialize Speech-to-Text model"""
        try:
            import whisper
            model_name = os.getenv("STT_MODEL", "base")
            self.stt_model = whisper.load_model(model_name)
            logger.info(f"STT model loaded: {model_name}")
        except ImportError:
            logger.warning("Whisper not available. Install with: pip install openai-whisper")
            self.stt_model = None
        except Exception as e:
            logger.error(f"Error loading STT model: {e}")
            self.stt_model = None
    
    def _init_tts(self):
        """Initialize Text-to-Speech model"""
        try:
            from TTS.api import TTS
            model_name = os.getenv("TTS_MODEL", "tts_models/en/ljspeech/tacotron2-DDC")
            
            # Initialize TTS
            self.tts_model = TTS(model_name=model_name)
            logger.info(f"TTS model loaded: {model_name}")
            
        except ImportError:
            logger.warning("TTS not available. Install with: pip install TTS")
            self.tts_model = None
        except Exception as e:
            logger.error(f"Error loading TTS model: {e}")
            self.tts_model = None
    
    def transcribe_audio(self, audio_file: str) -> Dict[str, Any]:
        """Transcribe audio file to text using Whisper"""
        try:
            if not self.stt_model:
                return {
                    "success": False,
                    "error": "STT model not available",
                    "text": "",
                    "confidence": 0.0
                }
            
            # Load and transcribe audio
            result = self.stt_model.transcribe(audio_file)
            
            return {
                "success": True,
                "text": result["text"].strip(),
                "confidence": result.get("confidence", 0.0),
                "language": result.get("language", "en"),
                "segments": result.get("segments", [])
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0
            }
    
    def transcribe_audio_data(self, audio_data: bytes) -> Dict[str, Any]:
        """Transcribe audio data directly"""
        try:
            if not self.stt_model:
                return {
                    "success": False,
                    "error": "STT model not available",
                    "text": "",
                    "confidence": 0.0
                }
            
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Transcribe the temporary file
                result = self.transcribe_audio(temp_file_path)
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Error transcribing audio data: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0
            }
    
    def text_to_speech(self, text: str, output_file: Optional[str] = None, 
                      voice: Optional[str] = None) -> Dict[str, Any]:
        """Convert text to speech using Coqui TTS"""
        try:
            if not self.tts_model:
                return {
                    "success": False,
                    "error": "TTS model not available",
                    "audio_file": None,
                    "duration": 0
                }
            
            # Generate output file path if not provided
            if not output_file:
                output_dir = Path("temp")
                output_dir.mkdir(exist_ok=True)
                output_file = str(output_dir / f"tts_{int(time.time())}.wav")
            
            # Generate speech
            self.tts_model.tts_to_file(
                text=text,
                file_path=str(output_file),
                speaker=voice or "default"
            )
            
            # Get audio duration
            duration = self._get_audio_duration(str(output_file))
            
            return {
                "success": True,
                "audio_file": str(output_file),
                "duration": duration,
                "text": text,
                "voice": voice or "default"
            }
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            return {
                "success": False,
                "error": str(e),
                "audio_file": None,
                "duration": 0
            }
    
    def text_to_speech_data(self, text: str, voice: Optional[str] = None) -> Dict[str, Any]:
        """Convert text to speech and return audio data"""
        try:
            if not self.tts_model:
                return {
                    "success": False,
                    "error": "TTS model not available",
                    "audio_data": None,
                    "duration": 0
                }
            
            # Generate speech to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file_path = temp_file.name
            
            try:
                # Generate speech
                self.tts_model.tts_to_file(
                    text=text,
                    file_path=temp_file_path,
                    speaker=voice or "default"
                )
                
                # Read audio data
                with open(temp_file_path, 'rb') as f:
                    audio_data = f.read()
                
                # Get duration
                duration = self._get_audio_duration(temp_file_path)
                
                return {
                    "success": True,
                    "audio_data": audio_data,
                    "duration": duration,
                    "text": text,
                    "voice": voice or "default"
                }
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
            
        except Exception as e:
            logger.error(f"Error in text-to-speech data: {e}")
            return {
                "success": False,
                "error": str(e),
                "audio_data": None,
                "duration": 0
            }
    
    def _get_audio_duration(self, audio_file: str) -> float:
        """Get duration of audio file in seconds"""
        try:
            with wave.open(audio_file, 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration = frames / float(rate)
                return duration
        except Exception as e:
            logger.warning(f"Could not get audio duration: {e}")
            return 0.0
    
    def record_audio(self, duration: int = 5, sample_rate: int = 16000) -> Dict[str, Any]:
        """Record audio from microphone"""
        try:
            import pyaudio
            
            # Audio recording parameters
            chunk = 1024
            channels = 1
            format_type = pyaudio.paInt16
            
            # Initialize PyAudio
            p = pyaudio.PyAudio()
            
            # Open stream
            stream = p.open(
                format=format_type,
                channels=channels,
                rate=sample_rate,
                input=True,
                frames_per_buffer=chunk
            )
            
            logger.info(f"Recording for {duration} seconds...")
            frames = []
            
            # Record audio
            for i in range(0, int(sample_rate / chunk * duration)):
                data = stream.read(chunk)
                frames.append(data)
            
            # Stop and close stream
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file_path = temp_file.name
            
            # Write WAV file
            with wave.open(temp_file_path, 'wb') as wav_file:
                wav_file.setnchannels(channels)
                wav_file.setsampwidth(p.get_sample_size(format_type))
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(b''.join(frames))
            
            return {
                "success": True,
                "audio_file": temp_file_path,
                "duration": duration,
                "sample_rate": sample_rate
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "PyAudio not available. Install with: pip install pyaudio",
                "audio_file": None,
                "duration": 0
            }
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            return {
                "success": False,
                "error": str(e),
                "audio_file": None,
                "duration": 0
            }
    
    def get_available_voices(self) -> Dict[str, Any]:
        """Get available TTS voices"""
        try:
            if not self.tts_model:
                return {
                    "success": False,
                    "error": "TTS model not available",
                    "voices": []
                }
            
            # Get available speakers
            speakers = self.tts_model.speakers if hasattr(self.tts_model, 'speakers') else []
            
            return {
                "success": True,
                "voices": speakers,
                "current_voice": "default"
            }
            
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return {
                "success": False,
                "error": str(e),
                "voices": []
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get voice interface status"""
        return {
            "stt_available": self.stt_model is not None,
            "tts_available": self.tts_model is not None,
            "audio_config": self.audio_config,
            "stt_model": os.getenv("STT_MODEL", "base") if self.stt_model else None,
            "tts_model": os.getenv("TTS_MODEL", "tts_models/en/ljspeech/tacotron2-DDC") if self.tts_model else None
        }

# Global voice interface instance
_voice_interface = None

def get_voice_interface() -> VoiceInterface:
    """Get global voice interface instance"""
    global _voice_interface
    if _voice_interface is None:
        _voice_interface = VoiceInterface()
    return _voice_interface

def transcribe_audio(audio_file: str) -> Dict[str, Any]:
    """Transcribe audio (convenience function)"""
    voice_interface = get_voice_interface()
    return voice_interface.transcribe_audio(audio_file)

def text_to_speech(text: str, output_file: Optional[str] = None, voice: Optional[str] = None) -> Dict[str, Any]:
    """Text to speech (convenience function)"""
    voice_interface = get_voice_interface()
    return voice_interface.text_to_speech(text, output_file, voice) 