"""
Atulya AI - Configuration Manager (v0.1.0)
Full production configuration management with validation
"""

import os
import yaml
import json
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime
import copy

# Configure logging
logger = logging.getLogger(__name__)

class ConfigManager:
    """Full production configuration manager for Atulya AI"""
    
    def __init__(self, config_path: str = "Config/config.yaml", env_file: str = ".env"):
        self.config_path = Path(config_path)
        self.env_file = Path(env_file)
        self.config = {}
        self.env_vars = {}
        self.validators = {}
        
        # Initialize configuration
        self._load_config()
        self._load_env_vars()
        self._setup_validators()
        self._validate_config()
    
    def _load_config(self):
        """Load configuration from YAML file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
                logger.info(f"Configuration loaded from {self.config_path}")
            else:
                logger.warning(f"Config file not found: {self.config_path}")
                self.config = self._get_default_config()
                
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config = self._get_default_config()
    
    def _load_env_vars(self):
        """Load environment variables"""
        try:
            # Load from .env file if it exists
            if self.env_file.exists():
                from dotenv import load_dotenv
                load_dotenv(self.env_file)
                logger.info(f"Environment variables loaded from {self.env_file}")
            
            # Get all relevant environment variables
            self.env_vars = {
                "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
                "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
                "HUGGINGFACE_TOKEN": os.getenv("HUGGINGFACE_TOKEN"),
                "DEFAULT_MODEL": os.getenv("DEFAULT_MODEL", "deepseek"),
                "FALLBACK_MODEL": os.getenv("FALLBACK_MODEL", "openai"),
                "MAX_TOKENS": int(os.getenv("MAX_TOKENS", "4096")),
                "TEMPERATURE": float(os.getenv("TEMPERATURE", "0.7")),
                "TOP_P": float(os.getenv("TOP_P", "0.9")),
                "HOST": os.getenv("HOST", "0.0.0.0"),
                "PORT": int(os.getenv("PORT", "8000")),
                "WEB_UI_PORT": int(os.getenv("WEB_UI_PORT", "8501")),
                "MEMORY_BACKEND": os.getenv("MEMORY_BACKEND", "chromadb"),
                "MEMORY_PATH": os.getenv("MEMORY_PATH", "./memory"),
                "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
                "LOG_FILE": os.getenv("LOG_FILE", "./logs/atulya.log"),
                "DEBUG": os.getenv("DEBUG", "true").lower() == "true",
                "RELOAD": os.getenv("RELOAD", "true").lower() == "true",
                "STT_MODEL": os.getenv("STT_MODEL", "base"),
                "TTS_MODEL": os.getenv("TTS_MODEL", "tts_models/en/ljspeech/tacotron2-DDC"),
                "AUDIO_SAMPLE_RATE": int(os.getenv("AUDIO_SAMPLE_RATE", "16000")),
                "AUDIO_CHANNELS": int(os.getenv("AUDIO_CHANNELS", "1")),
                "AUDIO_FORMAT": os.getenv("AUDIO_FORMAT", "wav"),
                "SECRET_KEY": os.getenv("SECRET_KEY", "your_secret_key_here_change_this_in_production"),
                "RATE_LIMIT_REQUESTS": int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
                "RATE_LIMIT_WINDOW": int(os.getenv("RATE_LIMIT_WINDOW", "3600"))
            }
            
        except Exception as e:
            logger.error(f"Error loading environment variables: {e}")
            self.env_vars = {}
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "models": {
                "deepseek": {
                    "type": "api",
                    "provider": "deepseek",
                    "model": "deepseek-chat",
                    "enabled": True,
                    "base_url": "https://api.deepseek.com/v1"
                },
                "openai": {
                    "type": "api",
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "enabled": True,
                    "base_url": "https://api.openai.com/v1"
                }
            },
            "default_model": "deepseek",
            "fallback_model": "openai",
            "parameters": {
                "max_tokens": 4096,
                "temperature": 0.7,
                "top_p": 0.9
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "web_ui_port": 8501,
                "debug": True,
                "reload": True
            },
            "memory": {
                "backend": "chromadb",
                "path": "./memory",
                "max_size": 1000,
                "ttl": 86400
            },
            "logging": {
                "level": "INFO",
                "file": "./logs/atulya.log",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "voice": {
                "stt_model": "base",
                "tts_model": "tts_models/en/ljspeech/tacotron2-DDC",
                "sample_rate": 16000,
                "channels": 1,
                "format": "wav"
            },
            "security": {
                "secret_key": "your_secret_key_here_change_this_in_production",
                "rate_limit_requests": 100,
                "rate_limit_window": 3600
            },
            "tools": {
                "file_io": True,
                "web_search": True,
                "code_execution": False,
                "calendar": False,
                "email": False
            }
        }
    
    def _setup_validators(self):
        """Setup configuration validators"""
        self.validators = {
            "models": self._validate_models,
            "server": self._validate_server,
            "memory": self._validate_memory,
            "logging": self._validate_logging,
            "voice": self._validate_voice,
            "security": self._validate_security,
            "tools": self._validate_tools
        }
    
    def _validate_config(self):
        """Validate the entire configuration"""
        try:
            for section, validator in self.validators.items():
                if section in self.config:
                    validator(self.config[section])
            
            logger.info("Configuration validation passed")
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            # Use default config on validation failure
            self.config = self._get_default_config()
    
    def _validate_models(self, models_config: Dict[str, Any]):
        """Validate models configuration"""
        required_fields = ["type", "provider", "model", "enabled"]
        
        for model_name, model_config in models_config.items():
            for field in required_fields:
                if field not in model_config:
                    raise ValueError(f"Model {model_name} missing required field: {field}")
            
            if not isinstance(model_config["enabled"], bool):
                raise ValueError(f"Model {model_name} enabled field must be boolean")
    
    def _validate_server(self, server_config: Dict[str, Any]):
        """Validate server configuration"""
        if "port" in server_config and not (1 <= server_config["port"] <= 65535):
            raise ValueError("Server port must be between 1 and 65535")
        
        if "web_ui_port" in server_config and not (1 <= server_config["web_ui_port"] <= 65535):
            raise ValueError("Web UI port must be between 1 and 65535")
    
    def _validate_memory(self, memory_config: Dict[str, Any]):
        """Validate memory configuration"""
        valid_backends = ["chromadb", "sqlite", "redis"]
        if memory_config.get("backend") not in valid_backends:
            raise ValueError(f"Memory backend must be one of: {valid_backends}")
    
    def _validate_logging(self, logging_config: Dict[str, Any]):
        """Validate logging configuration"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if logging_config.get("level") not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
    
    def _validate_voice(self, voice_config: Dict[str, Any]):
        """Validate voice configuration"""
        if voice_config.get("sample_rate") and voice_config["sample_rate"] <= 0:
            raise ValueError("Audio sample rate must be positive")
        
        if voice_config.get("channels") and voice_config["channels"] not in [1, 2]:
            raise ValueError("Audio channels must be 1 or 2")
    
    def _validate_security(self, security_config: Dict[str, Any]):
        """Validate security configuration"""
        if len(security_config.get("secret_key", "")) < 32:
            logger.warning("Secret key is too short. Consider using a longer key in production.")
    
    def _validate_tools(self, tools_config: Dict[str, Any]):
        """Validate tools configuration"""
        for tool_name, enabled in tools_config.items():
            if not isinstance(enabled, bool):
                raise ValueError(f"Tool {tool_name} enabled field must be boolean")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        # Check environment variables first
        if key.upper() in self.env_vars:
            return self.env_vars[key.upper()]
        
        # Check config file
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific model"""
        models = self.get("models", {})
        return models.get(model_name)
    
    def get_enabled_models(self) -> List[str]:
        """Get list of enabled models"""
        models = self.get("models", {})
        return [name for name, config in models.items() if config.get("enabled", False)]
    
    def is_model_enabled(self, model_name: str) -> bool:
        """Check if a model is enabled"""
        model_config = self.get_model_config(model_name)
        return model_config.get("enabled", False) if model_config else False
    
    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration"""
        return self.get("server", {})
    
    def get_memory_config(self) -> Dict[str, Any]:
        """Get memory configuration"""
        return self.get("memory", {})
    
    def get_voice_config(self) -> Dict[str, Any]:
        """Get voice configuration"""
        return self.get("voice", {})
    
    def get_tools_config(self) -> Dict[str, Any]:
        """Get tools configuration"""
        return self.get("tools", {})
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a tool is enabled"""
        tools = self.get_tools_config()
        return tools.get(tool_name, False)
    
    def save_config(self, file_path: Optional[str] = None):
        """Save configuration to file"""
        try:
            save_path = Path(file_path) if file_path else self.config_path
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {save_path}")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def export_config(self, format: str = "json") -> str:
        """Export configuration in specified format"""
        try:
            if format.lower() == "json":
                return json.dumps(self.config, indent=2)
            elif format.lower() == "yaml":
                return yaml.dump(self.config, default_flow_style=False, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting configuration: {e}")
            return ""
    
    def import_config(self, config_data: Union[str, Dict[str, Any]], format: str = "json"):
        """Import configuration from data"""
        try:
            if isinstance(config_data, str):
                if format.lower() == "json":
                    new_config = json.loads(config_data)
                elif format.lower() == "yaml":
                    new_config = yaml.safe_load(config_data)
                else:
                    raise ValueError(f"Unsupported format: {format}")
            else:
                new_config = config_data
            
            # Validate the new configuration
            old_config = self.config
            self.config = new_config
            self._validate_config()
            
            logger.info("Configuration imported successfully")
            
        except Exception as e:
            logger.error(f"Error importing configuration: {e}")
            self.config = old_config
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            "config_file": str(self.config_path),
            "env_file": str(self.env_file),
            "default_model": self.get("default_model"),
            "fallback_model": self.get("fallback_model"),
            "enabled_models": self.get_enabled_models(),
            "server": self.get_server_config(),
            "memory_backend": self.get("memory.backend"),
            "enabled_tools": [name for name, enabled in self.get_tools_config().items() if enabled],
            "voice_enabled": self.get("voice.stt_model") and self.get("voice.tts_model"),
            "debug_mode": self.get("server.debug", False),
            "last_updated": datetime.now().isoformat()
        }
    
    def reload_config(self):
        """Reload configuration from files"""
        self._load_config()
        self._load_env_vars()
        self._validate_config()
        logger.info("Configuration reloaded")

# Global configuration manager instance
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value (convenience function)"""
    config_manager = get_config_manager()
    return config_manager.get(key, default) 