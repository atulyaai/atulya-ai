"""
Atulya AI - Tool Registry (v0.1.0)
Auto-discovery and management of tools
"""

import os
import logging
import importlib
import inspect
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class ToolRegistry:
    """Tool registry for auto-discovery and management"""
    
    def __init__(self, tools_path: str = "Utilies/Tools"):
        self.tools_path = Path(tools_path)
        self.tools = {}
        self.tool_metadata = {}
        self.initialized = False
        
        # Initialize registry
        self._init_registry()
    
    def _init_registry(self):
        """Initialize the tool registry"""
        try:
            # Create tools directory if it doesn't exist
            self.tools_path.mkdir(parents=True, exist_ok=True)
            
            # Discover and load tools
            self._discover_tools()
            
            self.initialized = True
            logger.info(f"Tool registry initialized with {len(self.tools)} tools")
            
        except Exception as e:
            logger.error(f"Error initializing tool registry: {e}")
            self.initialized = False
    
    def _discover_tools(self):
        """Discover available tools"""
        try:
            # Look for tool files in the tools directory
            for tool_file in self.tools_path.glob("*.py"):
                if tool_file.name.startswith("__"):
                    continue
                
                self._load_tool_file(tool_file)
                
        except Exception as e:
            logger.error(f"Error discovering tools: {e}")
    
    def _load_tool_file(self, tool_file: Path):
        """Load tools from a Python file"""
        try:
            # Import the module
            module_name = f"Utilies.Tools.{tool_file.stem}"
            
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                logger.warning(f"Could not import {module_name}")
                return
            
            # Look for tool functions
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) and hasattr(obj, '_is_tool'):
                    self._register_tool(name, obj)
                    
        except Exception as e:
            logger.error(f"Error loading tool file {tool_file}: {e}")
    
    def _register_tool(self, name: str, tool_func: Callable):
        """Register a tool function"""
        try:
            # Get tool metadata
            metadata = getattr(tool_func, '_tool_metadata', {})
            
            self.tools[name] = tool_func
            self.tool_metadata[name] = {
                "name": name,
                "description": metadata.get("description", ""),
                "category": metadata.get("category", "general"),
                "parameters": metadata.get("parameters", {}),
                "function": tool_func
            }
            
            logger.info(f"Registered tool: {name}")
            
        except Exception as e:
            logger.error(f"Error registering tool {name}: {e}")
    
    def get_available_tools(self) -> Dict[str, Any]:
        """Get all available tools"""
        return self.tools.copy()
    
    def get_tool_metadata(self) -> Dict[str, Any]:
        """Get metadata for all tools"""
        return self.tool_metadata.copy()
    
    def get_tool(self, tool_name: str) -> Optional[Callable]:
        """Get a specific tool by name"""
        return self.tools.get(tool_name)
    
    def execute_tool(self, tool_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a tool with given arguments"""
        try:
            tool = self.get_tool(tool_name)
            if not tool:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not found"
                }
            
            # Execute the tool
            result = tool(*args, **kwargs)
            
            return {
                "success": True,
                "tool": tool_name,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }
    
    def list_tools_by_category(self, category: str) -> List[str]:
        """List tools by category"""
        return [
            name for name, metadata in self.tool_metadata.items()
            if metadata.get("category") == category
        ]
    
    def search_tools(self, query: str) -> List[str]:
        """Search tools by name or description"""
        query_lower = query.lower()
        matching_tools = []
        
        for name, metadata in self.tool_metadata.items():
            if (query_lower in name.lower() or 
                query_lower in metadata.get("description", "").lower()):
                matching_tools.append(name)
        
        return matching_tools
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a tool"""
        return self.tool_metadata.get(tool_name)
    
    def register_tool(self, name: str, func: Callable, metadata: Optional[Dict[str, Any]] = None):
        """Manually register a tool"""
        try:
            self._register_tool(name, func)
            if metadata:
                self.tool_metadata[name].update(metadata)
                
        except Exception as e:
            logger.error(f"Error manually registering tool {name}: {e}")
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool"""
        try:
            if tool_name in self.tools:
                del self.tools[tool_name]
                del self.tool_metadata[tool_name]
                logger.info(f"Unregistered tool: {tool_name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error unregistering tool {tool_name}: {e}")
            return False
    
    def reload_tools(self):
        """Reload all tools"""
        try:
            self.tools.clear()
            self.tool_metadata.clear()
            self._discover_tools()
            logger.info("Tools reloaded")
            
        except Exception as e:
            logger.error(f"Error reloading tools: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get tool registry status"""
        return {
            "initialized": self.initialized,
            "total_tools": len(self.tools),
            "categories": list(set(
                metadata.get("category", "general") 
                for metadata in self.tool_metadata.values()
            )),
            "tools_path": str(self.tools_path)
        }

# Decorator for registering tools
def tool(description: str = "", category: str = "general", parameters: Optional[Dict[str, Any]] = None):
    """Decorator to mark a function as a tool"""
    def decorator(func):
        func._is_tool = True
        func._tool_metadata = {
            "description": description,
            "category": category,
            "parameters": parameters or {}
        }
        return func
    return decorator

# Global tool registry instance
_tool_registry = None

def get_tool_registry() -> ToolRegistry:
    """Get global tool registry instance"""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry

def register_tool(name: str, func: Callable, metadata: Optional[Dict[str, Any]] = None):
    """Register a tool (convenience function)"""
    registry = get_tool_registry()
    registry.register_tool(name, func, metadata)

def execute_tool(tool_name: str, *args, **kwargs) -> Dict[str, Any]:
    """Execute a tool (convenience function)"""
    registry = get_tool_registry()
    return registry.execute_tool(tool_name, *args, **kwargs) 