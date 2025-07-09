"""
Atulya AI - Dynamic Intelligent Agent (v0.1.0)
DeepSeek R1 as main brain with dynamic delegation to specialized models/tools
"""

import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

# Import our dynamic components
try:
    from Core.model_loader import model_loader, analyze_and_execute
    MODEL_LOADER_AVAILABLE = True
except ImportError:
    MODEL_LOADER_AVAILABLE = False
    model_loader = None

try:
    from Core.memory import memory_manager
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    # Create placeholder memory manager
    class PlaceholderMemory:
        def get_user_profile(self, user_id: str):
            return {}
        def get_recent_interactions(self, user_id: str, limit: int = 3):
            return []
        def store_interaction(self, interaction: Dict):
            pass
        def get_status(self):
            return {"status": "placeholder"}
    memory_manager = PlaceholderMemory()

try:
    from Tools.tool_registry import tool_registry
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False
    # Create placeholder tool registry
    class PlaceholderToolRegistry:
        def get_tool(self, tool_name: str):
            return None
        def get_available_tools(self):
            return []
    tool_registry = PlaceholderToolRegistry()

class IntelligentAgent:
    """Dynamic intelligent agent with DeepSeek R1 as main brain"""
    
    def __init__(self, config_path: str = "Config/config.yaml"):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.memory = memory_manager
        self.tools = tool_registry
        self.model_loader = model_loader
        
        # Dynamic state
        self.conversation_history = []
        self.active_models = {}
        self.task_queue = []
        self.context = {}
        
        self.logger.info("Intelligent Agent initialized with dynamic capabilities")
    
    async def process_input(self, user_input: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Main brain processes input and dynamically delegates to appropriate models/tools
        """
        try:
        # Add to conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "input": user_input,
                "type": "user"
            })
            
            # Let DeepSeek R1 analyze the input and create execution plan
            analysis_result = await self.analyze_and_plan(user_input, user_id)
            
            # Execute the plan dynamically
            execution_result = await self.execute_plan(analysis_result, user_input, user_id)
            
            # Store interaction in memory
            await self.store_interaction(user_input, execution_result, user_id)
            
            return {
                "success": True,
                "response": execution_result.get("response", ""),
                "analysis": analysis_result,
                "execution_details": execution_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error processing your request. Let me try a different approach.",
                "timestamp": datetime.now().isoformat()
            }
    
    async def analyze_and_plan(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """
        Use DeepSeek R1 to analyze input and create dynamic execution plan
        """
        # Get user context and conversation history
        context = await self.get_user_context(user_id)
        recent_history = self.conversation_history[-5:]  # Last 5 interactions
        
        analysis_prompt = f"""
        You are Atulya AI's main brain. Analyze this user request and create a dynamic execution plan.
        
        User Request: "{user_input}"
        User Context: {json.dumps(context, indent=2)}
        Recent Conversation: {json.dumps(recent_history, indent=2)}
        
        Available capabilities:
        - text: General reasoning, conversation, analysis
        - vision: Image analysis, object detection, captioning
        - speech_input: Convert speech to text
        - speech_output: Convert text to speech
        - video: Video analysis and processing
        - document: PDF/document processing
        - audio_generation: Create music or sounds
        - embedding: Search, similarity, memory operations
        - tools: File operations, web search, email, calendar, code execution
        
        Create a comprehensive execution plan with:
        {{
            "intent": "what the user wants to achieve",
            "complexity": "simple|moderate|complex",
            "primary_capability": "main capability needed",
            "additional_capabilities": ["list of other needed capabilities"],
            "tools_needed": ["list of tools required"],
            "execution_steps": [
                {{
                    "step": 1,
                    "action": "what to do",
                    "capability": "which capability to use",
                    "tool": "specific tool if needed",
                    "depends_on": []
                }}
            ],
            "memory_operations": {{
                "retrieve": ["what to search in memory"],
                "store": "what to remember about this interaction"
            }},
            "admin_access_needed": false,
            "estimated_time": "quick|moderate|long",
            "confidence": 0.95
        }}
        
        Be intelligent about delegation - only use specialized models/tools when actually needed.
        """
        
        try:
            # Use main brain for analysis
            plan_response = await self.get_main_brain_response(analysis_prompt)
            plan = self.parse_execution_plan(plan_response)
            
            self.logger.info(f"Execution plan created: {plan['intent']}")
            return plan
            
        except Exception as e:
            self.logger.error(f"Planning failed: {e}")
            return self.create_fallback_plan(user_input)
    
    async def execute_plan(self, plan: Dict[str, Any], user_input: str, user_id: str) -> Dict[str, Any]:
        """
        Dynamically execute the plan using appropriate models and tools
        """
        execution_results = {
            "plan_executed": plan,
            "steps_completed": [],
            "models_used": [],
            "tools_used": [],
            "response": "",
            "success": True
        }
        
        try:
            # Load required models dynamically
            required_models = await self.load_required_models(plan)
            execution_results["models_used"] = list(required_models.keys())
            
            # Execute steps in order
            for step in plan.get("execution_steps", []):
                step_result = await self.execute_step(step, plan, user_input, user_id, required_models)
                execution_results["steps_completed"].append(step_result)
                
                if step_result.get("tool_used"):
                    execution_results["tools_used"].append(step_result["tool_used"])
            
            # Generate final response
            final_response = await self.generate_final_response(execution_results, user_input, plan)
            execution_results["response"] = final_response
            
            # Cleanup unused models to free memory
            await self.cleanup_models(plan)
            
            return execution_results
            
        except Exception as e:
            self.logger.error(f"Execution failed: {e}")
            execution_results["success"] = False
            execution_results["error"] = str(e)
            execution_results["response"] = await self.get_fallback_response(user_input)
            return execution_results
    
    async def execute_step(self, step: Dict, plan: Dict, user_input: str, user_id: str, models: Dict) -> Dict[str, Any]:
        """
        Execute a single step in the plan
        """
        try:
            action = step.get("action", "")
            capability = step.get("capability", "text")
            tool = step.get("tool")
            
            step_result = {
                "step_number": step.get("step", 0),
                "action": action,
                "capability": capability,
                "success": True,
                "result": "",
                "tool_used": tool
            }
            
            # Execute based on capability type
            if tool:
                # Use a tool
                step_result["result"] = await self.use_tool(tool, user_input, plan)
            elif capability == "vision":
                step_result["result"] = await self.process_vision(user_input, models.get("vision"))
            elif capability == "speech_input":
                step_result["result"] = await self.process_speech_input(user_input, models.get("speech_input"))
            elif capability == "speech_output":
                step_result["result"] = await self.process_speech_output(user_input, models.get("speech_output"))
            elif capability == "embedding":
                step_result["result"] = await self.process_embedding(user_input, models.get("embedding"))
            else:
                # Use main brain for text processing
                step_result["result"] = await self.process_with_main_brain(action, user_input, plan)
            
            return step_result
            
        except Exception as e:
            self.logger.error(f"Step execution failed: {e}")
            return {
                "step_number": step.get("step", 0),
                "action": step.get("action", ""),
                "success": False,
                "error": str(e),
                "result": ""
            }
    
    async def get_main_brain_response(self, prompt: str) -> str:
        """Get response from main brain (DeepSeek R1)"""
        try:
            if MODEL_LOADER_AVAILABLE and self.model_loader and hasattr(self.model_loader, 'main_brain'):
                main_brain = self.model_loader.main_brain
                if main_brain and main_brain.get("type") == "text":
                    # Simplified response for now - full model generation would be implemented here
                    return f"Analyzing request: {prompt[:50]}... -> AI processing complete"
                else:
                    return f"I understand you want: {prompt[:100]}..."
            else:
                return f"Processing your request: {prompt[:50]}..."
        except Exception as e:
            self.logger.error(f"Main brain response failed: {e}")
            return "I'm processing your request..."
    
    async def use_tool(self, tool_name: str, input_data: str, context: Dict) -> str:
        """Use a specific tool"""
        try:
            tool_function = self.tools.get_tool(tool_name)
            if tool_function:
                result = await tool_function(input_data, context)
                return str(result)
            else:
                return f"Tool {tool_name} not found"
        except Exception as e:
            self.logger.error(f"Tool usage failed: {e}")
            return f"Error using tool {tool_name}: {e}"
    
    async def process_vision(self, input_data: str, vision_model: Optional[Dict[str, Any]]) -> str:
        """Process vision input"""
        if not vision_model:
            return "Vision capability not available"
        
        try:
            # Process image if provided
            # This would be implemented based on the specific vision model
            return "Vision processing completed"
        except Exception as e:
            return f"Vision processing failed: {e}"
    
    async def process_speech_input(self, input_data: str, speech_model: Optional[Dict[str, Any]]) -> str:
        """Process speech input"""
        if not speech_model:
            return "Speech input capability not available"
        
        try:
            # Process audio if provided
            return "Speech processing completed"
        except Exception as e:
            return f"Speech processing failed: {e}"
    
    async def process_speech_output(self, text: str, tts_model: Optional[Dict[str, Any]]) -> str:
        """Generate speech output"""
        if not tts_model:
            return "Speech output capability not available"
        
        try:
            # Generate audio from text
            return "Speech generation completed"
        except Exception as e:
            return f"Speech generation failed: {e}"
    
    async def process_embedding(self, input_data: str, embedding_model: Optional[Dict[str, Any]]) -> str:
        """Process embedding operations"""
        if not embedding_model:
            return "Embedding capability not available"
        
        try:
            # Generate embeddings and perform search/similarity
            return "Embedding processing completed"
        except Exception as e:
            return f"Embedding processing failed: {e}"
    
    async def process_with_main_brain(self, action: str, user_input: str, context: Dict) -> str:
        """Process with main brain"""
        prompt = f"Action: {action}\nUser Input: {user_input}\nContext: {json.dumps(context)}\n\nProvide a helpful response:"
        return await self.get_main_brain_response(prompt)
    
    async def load_required_models(self, plan: Dict) -> Dict[str, Any]:
        """Load only the models needed for this plan"""
        required_models = {}
        
        if not MODEL_LOADER_AVAILABLE or not self.model_loader:
            return required_models
        
        # Get capabilities needed
        capabilities = [plan.get("primary_capability")]
        capabilities.extend(plan.get("additional_capabilities", []))
        
        # Load models for each capability
        for capability in capabilities:
            if capability and capability != "tools":
                try:
                    model = self.model_loader.load_model(capability)
                    if model:
                        required_models[capability] = model
                except Exception as e:
                    self.logger.warning(f"Failed to load model for {capability}: {e}")
        
        return required_models
    
    async def cleanup_models(self, plan: Dict):
        """Clean up models after execution"""
        if not MODEL_LOADER_AVAILABLE or not self.model_loader:
            return
        
        # Keep main brain and frequently used models
        keep_models = ["deepseek-r1"]
        
        # Add models that might be used again soon
        if plan.get("complexity") == "complex":
            keep_models.extend(["embedding", "text"])
        
        try:
            self.model_loader.unload_unused_models(keep_models)
        except Exception as e:
            self.logger.warning(f"Failed to cleanup models: {e}")
    
    async def generate_final_response(self, execution_results: Dict, user_input: str, plan: Dict) -> str:
        """Generate final response based on execution results"""
        response_prompt = f"""
        Generate a helpful response to the user based on these execution results:
        
        User Input: "{user_input}"
        Plan Intent: {plan.get('intent', '')}
        Steps Completed: {len(execution_results.get('steps_completed', []))}
        Success: {execution_results.get('success', False)}
        
        Step Results:
        {json.dumps(execution_results.get('steps_completed', []), indent=2)}
        
        Provide a clear, helpful response to the user:
        """
        
        return await self.get_main_brain_response(response_prompt)
    
    async def get_fallback_response(self, user_input: str) -> str:
        """Get fallback response when main processing fails"""
        return f"I understand your request about '{user_input[:50]}...' but encountered some technical difficulties. Let me try to help in a different way."
    
    def parse_execution_plan(self, response: str) -> Dict[str, Any]:
        """Parse execution plan from main brain response"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self.create_fallback_plan("")
        except Exception as e:
            self.logger.warning(f"Plan parsing failed: {e}")
            return self.create_fallback_plan("")
    
    def create_fallback_plan(self, user_input: str) -> Dict[str, Any]:
        """Create fallback plan when analysis fails"""
        return {
            "intent": "Respond to user request",
            "complexity": "simple",
            "primary_capability": "text",
            "additional_capabilities": [],
            "tools_needed": [],
            "execution_steps": [
                {
                    "step": 1,
                    "action": "Generate helpful response",
                    "capability": "text",
                    "depends_on": []
                }
            ],
            "memory_operations": {
                "retrieve": [],
                "store": "User interaction"
            },
            "admin_access_needed": False,
            "estimated_time": "quick",
            "confidence": 0.5
        }
    
    async def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user context from memory"""
        try:
            if MEMORY_AVAILABLE and hasattr(self.memory, 'get_user_profile'):
                user_profile = self.memory.get_user_profile(user_id)
                recent_interactions = self.memory.get_recent_interactions(user_id, limit=3)
            else:
                user_profile = {}
                recent_interactions = []
            
            return {
                "profile": user_profile,
                "recent_interactions": recent_interactions,
                "conversation_length": len(self.conversation_history)
            }
        except Exception as e:
            self.logger.warning(f"Failed to get user context: {e}")
            return {"profile": {}, "recent_interactions": [], "conversation_length": 0}
    
    async def store_interaction(self, user_input: str, execution_result: Dict, user_id: str):
        """Store interaction in memory"""
        try:
            interaction = {
                "user_id": user_id,
                "input": user_input,
                "response": execution_result.get("response", ""),
                "timestamp": datetime.now().isoformat(),
                "success": execution_result.get("success", False),
                "models_used": execution_result.get("models_used", []),
                "tools_used": execution_result.get("tools_used", [])
            }
            
            if MEMORY_AVAILABLE and hasattr(self.memory, 'store_interaction'):
                self.memory.store_interaction(interaction)
            
        except Exception as e:
            self.logger.warning(f"Failed to store interaction: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            "agent_status": "active",
            "conversation_length": len(self.conversation_history),
            "task_queue_length": len(self.task_queue),
            "dynamic_mode": True,
            "timestamp": datetime.now().isoformat()
        }
        
        if MODEL_LOADER_AVAILABLE and self.model_loader:
            try:
                status["main_brain_active"] = self.model_loader.main_brain is not None
                status["model_status"] = self.model_loader.get_system_status()
            except Exception as e:
                status["model_status"] = {"error": str(e)}
        else:
            status["main_brain_active"] = False
            status["model_status"] = {"status": "not_available"}
        
        if MEMORY_AVAILABLE and hasattr(self.memory, 'get_status'):
            try:
                status["memory_status"] = self.memory.get_status()
            except Exception as e:
                status["memory_status"] = {"error": str(e)}
        else:
            status["memory_status"] = {"status": "not_available"}
        
        if TOOLS_AVAILABLE and hasattr(self.tools, 'get_available_tools'):
            try:
                status["tools_available"] = len(self.tools.get_available_tools())
            except Exception as e:
                status["tools_available"] = 0
        else:
            status["tools_available"] = 0
        
        return status
    
    async def process_admin_request(self, request: str, user_id: str) -> Dict[str, Any]:
        """Process admin requests dynamically"""
        admin_prompt = f"""
        Process this admin request dynamically:
        
        Request: "{request}"
        User: {user_id}
        Current System Status: {json.dumps(self.get_system_status(), indent=2)}
        
        Determine what admin actions are needed and execute them safely.
        Consider: model management, system health, user permissions, configuration changes.
        
        Return a JSON response with the results.
        """
        
        try:
            response = await self.get_main_brain_response(admin_prompt)
            return {"success": True, "admin_response": response}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global agent instance
intelligent_agent = IntelligentAgent()

async def process_user_input(user_input: str, user_id: str = "default") -> Dict[str, Any]:
    """Main function to process user input"""
    return await intelligent_agent.process_input(user_input, user_id)

def get_system_status() -> Dict[str, Any]:
    """Get system status"""
    return intelligent_agent.get_system_status() 