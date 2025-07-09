"""
Atulya AI - Dynamic Model Loader (v0.1.0)
Intelligently loads and manages models on demand
DeepSeek R1 acts as the main brain and delegates to specialized models
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import importlib

# Try to import optional dependencies
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

class DynamicModelLoader:
    """Dynamic model loader that loads models on demand"""
    
    def __init__(self, config_path: str = "Config/config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
        self.loaded_models: Dict[str, Any] = {}
        self.main_brain: Optional[Dict[str, Any]] = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize main brain (DeepSeek R1)
        self.initialize_main_brain()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
                self.logger.info(f"Configuration loaded from {self.config_path}")
                return config
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return {}
    
    def initialize_main_brain(self) -> None:
        """Initialize the main brain (DeepSeek R1) that delegates tasks"""
        try:
            primary_model = self.config.get('model', {}).get('primary', 'deepseek-r1')
            self.main_brain = self.load_model(primary_model)
            self.logger.info("Main brain (DeepSeek R1) initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize main brain: {e}")
    
    def analyze_task(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Use DeepSeek R1 to analyze the task and determine which models to use
        Returns a plan with required models and their roles
        """
        analysis_prompt = f"""
        Analyze this user request and determine which AI capabilities are needed:
        
        User Request: "{user_input}"
        Context: {context or {}}
        
        Available capabilities:
        - text: General text processing, reasoning, chat
        - vision: Image analysis, captioning
        - speech_input: Convert speech to text
        - speech_output: Convert text to speech
        - video: Analyze video content
        - document: Process PDFs, extract text/structure
        - audio_generation: Create music or sounds
        - embedding: Search, similarity, memory
        
        Return a JSON with:
        {{
            "primary_capability": "main capability needed",
            "additional_capabilities": ["list", "of", "other", "needed", "capabilities"],
            "reasoning": "why these capabilities are needed",
            "confidence": 0.95
        }}
        """
        
        try:
            if self.main_brain:
                response = self.get_main_brain_response(analysis_prompt)
                # Parse the response to extract the plan
                plan = self.parse_task_analysis(response)
                self.logger.info(f"Task analysis complete: {plan}")
                return plan
            else:
                # Fallback: basic text processing
                return {
                    "primary_capability": "text",
                    "additional_capabilities": [],
                    "reasoning": "Main brain not available, using text fallback",
                    "confidence": 0.5
                }
        except Exception as e:
            self.logger.error(f"Task analysis failed: {e}")
            return {
                "primary_capability": "text",
                "additional_capabilities": [],
                "reasoning": f"Analysis failed: {e}",
                "confidence": 0.1
            }
    
    def get_main_brain_response(self, prompt: str) -> str:
        """Get response from main brain"""
        try:
            if self.main_brain and self.main_brain.get("type") == "text":
                # Simplified response for now - in production this would use the actual model
                return f"Analyzing: {prompt[:100]}... -> {{'primary_capability': 'text', 'confidence': 0.8}}"
            else:
                return "Main brain not available"
        except Exception as e:
            self.logger.error(f"Main brain response failed: {e}")
            return "Error in main brain"
    
    def parse_task_analysis(self, response: str) -> Dict[str, Any]:
        """Parse the task analysis response from DeepSeek R1"""
        try:
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                return plan
            else:
                # Fallback parsing
                return self.fallback_parse(response)
        except Exception as e:
            self.logger.warning(f"Failed to parse task analysis: {e}")
            return self.fallback_parse(response)
    
    def fallback_parse(self, response: str) -> Dict[str, Any]:
        """Fallback parsing when JSON parsing fails"""
        response_lower = response.lower()
        
        capabilities = {
            "vision": ["image", "photo", "picture", "visual", "see", "look"],
            "speech_input": ["speech", "voice", "audio", "listen", "hear"],
            "speech_output": ["speak", "say", "voice", "tts", "text to speech"],
            "video": ["video", "movie", "clip", "recording"],
            "document": ["pdf", "document", "file", "text", "extract"],
            "audio_generation": ["music", "sound", "audio", "generate", "create"],
            "embedding": ["search", "similar", "find", "memory"]
        }
        
        detected = []
        for capability, keywords in capabilities.items():
            if any(keyword in response_lower for keyword in keywords):
                detected.append(capability)
        
        return {
            "primary_capability": detected[0] if detected else "text",
            "additional_capabilities": detected[1:] if len(detected) > 1 else [],
            "reasoning": "Keyword-based detection",
            "confidence": 0.7 if detected else 0.3
        }
    
    def load_model(self, model_name: str, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """Dynamically load a model only when needed"""
        if model_name in self.loaded_models and not force_reload:
            self.logger.info(f"Model {model_name} already loaded")
            return self.loaded_models[model_name]
        
        try:
            model_config = self.config.get('models', {}).get(model_name, {})
            if not model_config.get('enabled', False):
                self.logger.warning(f"Model {model_name} is disabled")
                return None
            
            model_path = model_config.get('model')
            use_case = model_config.get('use_case', 'general')
            
            self.logger.info(f"Loading model {model_name} for {use_case}")
            
            # Dynamic loading based on use case
            model = None
            if use_case == "general":
                model = self.load_text_model(model_path, model_config)
            elif use_case == "vision":
                model = self.load_vision_model(model_path)
            elif use_case == "speech_input":
                model = self.load_speech_input_model(model_path)
            elif use_case == "speech_output":
                model = self.load_speech_output_model(model_path)
            elif use_case == "video":
                model = self.load_video_model(model_path)
            elif use_case == "document":
                model = self.load_document_model(model_path)
            elif use_case == "audio_generation":
                model = self.load_audio_generation_model(model_path)
            elif use_case == "embedding":
                model = self.load_embedding_model(model_path)
            else:
                self.logger.error(f"Unknown use case: {use_case}")
                return None
            
            if model:
                self.loaded_models[model_name] = model
                self.logger.info(f"Model {model_name} loaded successfully")
            
            return model
            
        except Exception as e:
            self.logger.error(f"Failed to load model {model_name}: {e}")
            return None
    
    def load_text_model(self, model_path: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Load text generation model"""
        try:
            if not TORCH_AVAILABLE:
                self.logger.warning("PyTorch not available, cannot load text model")
                return {
                    "type": "text",
                    "config": config,
                    "status": "placeholder"
                }
            
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            return {
                "tokenizer": tokenizer,
                "model": model,
                "type": "text",
                "config": config
            }
        except Exception as e:
            self.logger.error(f"Failed to load text model: {e}")
            return None
    
    def load_vision_model(self, model_path: str) -> Optional[Dict[str, Any]]:
        """Load vision model"""
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            
            processor = BlipProcessor.from_pretrained(model_path)
            model = BlipForConditionalGeneration.from_pretrained(model_path)
            
            return {
                "processor": processor,
                "model": model,
                "type": "vision"
            }
        except Exception as e:
            self.logger.error(f"Failed to load vision model: {e}")
            return None
    
    def load_speech_input_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Load speech-to-text model"""
        try:
            import whisper
            
            model = whisper.load_model(model_name)
            
            return {
                "model": model,
                "type": "speech_input"
            }
        except Exception as e:
            self.logger.error(f"Failed to load speech input model: {e}")
            return None
    
    def load_speech_output_model(self, model_path: str) -> Optional[Dict[str, Any]]:
        """Load text-to-speech model"""
        try:
            from TTS.api import TTS
            
            tts = TTS(model_path)
            
            return {
                "model": tts,
                "type": "speech_output"
            }
        except Exception as e:
            self.logger.error(f"Failed to load speech output model: {e}")
            return None
    
    def load_video_model(self, model_path: str) -> Optional[Dict[str, Any]]:
        """Load video analysis model"""
        try:
            from transformers import VideoMAEProcessor, VideoMAEForVideoClassification
            
            processor = VideoMAEProcessor.from_pretrained(model_path)
            model = VideoMAEForVideoClassification.from_pretrained(model_path)
            
            return {
                "processor": processor,
                "model": model,
                "type": "video"
            }
        except Exception as e:
            self.logger.error(f"Failed to load video model: {e}")
            return None
    
    def load_document_model(self, model_path: str) -> Optional[Dict[str, Any]]:
        """Load document processing model"""
        try:
            from transformers import LayoutLMv3Processor, LayoutLMv3ForQuestionAnswering
            
            processor = LayoutLMv3Processor.from_pretrained(model_path)
            model = LayoutLMv3ForQuestionAnswering.from_pretrained(model_path)
            
            return {
                "processor": processor,
                "model": model,
                "type": "document"
            }
        except Exception as e:
            self.logger.error(f"Failed to load document model: {e}")
            return None
    
    def load_audio_generation_model(self, model_path: str) -> Optional[Dict[str, Any]]:
        """Load audio generation model"""
        try:
            from transformers import MusicgenProcessor, MusicgenForConditionalGeneration
            
            processor = MusicgenProcessor.from_pretrained(model_path)
            model = MusicgenForConditionalGeneration.from_pretrained(model_path)
            
            return {
                "processor": processor,
                "model": model,
                "type": "audio_generation"
            }
        except Exception as e:
            self.logger.error(f"Failed to load audio generation model: {e}")
            return None
    
    def load_embedding_model(self, model_path: str) -> Optional[Dict[str, Any]]:
        """Load embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            
            model = SentenceTransformer(model_path)
            
            return {
                "model": model,
                "type": "embedding"
            }
        except Exception as e:
            self.logger.error(f"Failed to load embedding model: {e}")
    return None 
    
    def get_models_for_task(self, task_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Load all models needed for a specific task"""
        required_models = {}
        
        # Load primary capability model
        primary = task_plan.get("primary_capability")
        if primary:
            model_name = self.config.get('model', {}).get(primary)
            if model_name:
                model = self.load_model(model_name)
                if model:
                    required_models[primary] = model
        
        # Load additional capability models
        additional = task_plan.get("additional_capabilities", [])
        for capability in additional:
            model_name = self.config.get('model', {}).get(capability)
            if model_name:
                model = self.load_model(model_name)
                if model:
                    required_models[capability] = model
        
        return required_models
    
    def unload_unused_models(self, keep_models: Optional[List[str]] = None) -> None:
        """Unload models not in the keep list to free memory"""
        keep_models = keep_models or ["deepseek-r1"]  # Always keep main brain
        
        to_unload = []
        for model_name in self.loaded_models:
            if model_name not in keep_models:
                to_unload.append(model_name)
        
        for model_name in to_unload:
            del self.loaded_models[model_name]
            self.logger.info(f"Unloaded model {model_name}")
        
        # Clear GPU cache if available
        if TORCH_AVAILABLE and torch and torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get dynamic system status"""
        return {
            "main_brain_active": self.main_brain is not None,
            "loaded_models": list(self.loaded_models.keys()),
            "available_models": list(self.config.get('models', {}).keys()),
            "memory_usage": self.get_memory_usage(),
            "gpu_available": TORCH_AVAILABLE and torch and torch.cuda.is_available(),
            "dynamic_loading": True
        }
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information"""
        system_memory = {"error": "psutil not available"}
        gpu_memory = {}
        
        if PSUTIL_AVAILABLE and psutil:
            try:
                memory = psutil.virtual_memory()
                system_memory = {
                    "total": memory.total,
                    "used": memory.used,
                    "available": memory.available,
                    "percent": memory.percent
                }
            except Exception as e:
                system_memory = {"error": str(e)}
        
        if TORCH_AVAILABLE and torch and torch.cuda.is_available():
            try:
                gpu_memory = {
                    "allocated": torch.cuda.memory_allocated(),
                    "cached": torch.cuda.memory_reserved(),
                    "total": torch.cuda.get_device_properties(0).total_memory
                }
            except Exception as e:
                gpu_memory = {"error": str(e)}
        
        return {
            "system_memory": system_memory,
            "gpu_memory": gpu_memory
        }

# Global instance
model_loader = DynamicModelLoader()

def load_model(model_name: str) -> Optional[Dict[str, Any]]:
    """Load a specific model"""
    return model_loader.load_model(model_name)

def analyze_and_execute(user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Main function to analyze task and execute with appropriate models"""
    # Let DeepSeek R1 analyze the task
    task_plan = model_loader.analyze_task(user_input, context)
    
    # Load required models
    required_models = model_loader.get_models_for_task(task_plan)
    
    return {
        "task_plan": task_plan,
        "models": required_models,
        "ready": len(required_models) > 0
    } 