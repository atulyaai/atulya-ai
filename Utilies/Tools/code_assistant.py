"""
Atulya AI - Code Assistant Tool
Supports OpenAI API and free alternatives
"""

import requests
import json
import os
from typing import Optional, Dict, Any, List

class CodeAssistant:
    """Code assistance tool with OpenAI API and free alternatives"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
    def get_openai_code_suggestion(self, code_context: str, language: str = "python") -> str:
        """Get code suggestion from OpenAI GPT-4"""
        if not self.openai_key:
            return "OpenAI API key not configured"
            
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are a helpful coding assistant. Provide {language} code suggestions."
                    },
                    {
                        "role": "user",
                        "content": f"Complete this {language} code:\n\n{code_context}"
                    }
                ],
                "max_tokens": 200,
                "temperature": 0.1
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                return f"OpenAI API error: {response.status_code}"
                
        except Exception as e:
            return f"OpenAI API error: {str(e)}"
    
    def get_claude_code_suggestion(self, code_context: str, language: str = "python") -> str:
        """Get code suggestion from Claude"""
        if not self.anthropic_key:
            return "Anthropic API key not configured"
            
        try:
            headers = {
                "x-api-key": self.anthropic_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 200,
                "messages": [
                    {
                        "role": "user",
                        "content": f"Complete this {language} code:\n\n{code_context}"
                    }
                ]
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("content", [{}])[0].get("text", "")
            else:
                return f"Claude API error: {response.status_code}"
                
        except Exception as e:
            return f"Claude API error: {str(e)}"
    
    def get_free_code_suggestion(self, code_context: str, language: str = "python") -> str:
        """Get code suggestion using free alternatives"""
        # Simple template-based suggestions
        if "function" in code_context.lower():
            return f"""def example_function():
    \"\"\"Example function based on your request\"\"\"
    # TODO: Implement your logic here
    pass"""
        elif "class" in code_context.lower():
            return f"""class ExampleClass:
    \"\"\"Example class based on your request\"\"\"
    def __init__(self):
        pass"""
        else:
            return f"# {language} code suggestion:\n# {code_context}\n# TODO: Implement with local model"
    
    def suggest_code(self, code_context: str, language: str = "python", provider: str = "auto") -> str:
        """Get code suggestion from the best available provider"""
        
        if provider == "openai" and self.openai_key:
            return self.get_openai_code_suggestion(code_context, language)
        elif provider == "claude" and self.anthropic_key:
            return self.get_claude_code_suggestion(code_context, language)
        elif provider == "free":
            return self.get_free_code_suggestion(code_context, language)
        else:
            # Auto-select best available
            if self.openai_key:
                return self.get_openai_code_suggestion(code_context, language)
            elif self.anthropic_key:
                return self.get_claude_code_suggestion(code_context, language)
            else:
                return self.get_free_code_suggestion(code_context, language)
    
    def explain_code(self, code: str, language: str = "python") -> str:
        """Explain what the code does"""
        if self.openai_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "gpt-4",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful coding assistant. Explain code clearly and concisely."
                        },
                        {
                            "role": "user",
                            "content": f"Explain this {language} code:\n\n{code}"
                        }
                    ],
                    "max_tokens": 300,
                    "temperature": 0.1
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    return f"OpenAI API error: {response.status_code}"
                    
            except Exception as e:
                return f"OpenAI API error: {str(e)}"
        else:
            return f"# Code Explanation ({language}):\n# This code appears to be: {code[:100]}...\n# Add OpenAI API key for detailed explanation"
    
    def refactor_code(self, code: str, language: str = "python") -> str:
        """Suggest refactored version of the code"""
        if self.openai_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "gpt-4",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful coding assistant. Refactor code to be more readable and efficient."
                        },
                        {
                            "role": "user",
                            "content": f"Refactor this {language} code:\n\n{code}"
                        }
                    ],
                    "max_tokens": 400,
                    "temperature": 0.1
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    return f"OpenAI API error: {response.status_code}"
                    
            except Exception as e:
                return f"OpenAI API error: {str(e)}"
        else:
            return f"# Refactored {language} code:\n# Original: {code[:100]}...\n# Add OpenAI API key for refactoring"

# Global instance
code_assistant = CodeAssistant() 