"""
Atulya AI - Memory Manager (v0.1.0)
Basic episodic and semantic memory system
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class MemoryManager:
    """Basic memory manager for Atulya AI"""
    
    def __init__(self, memory_path: str = "./memory"):
        self.memory_path = Path(memory_path)
        self.episodic_memory = []
        self.semantic_memory = {}
        self.memory_file = self.memory_path / "memory.json"
        self.initialized = False
    
    def initialize(self):
        """Initialize the memory system"""
        try:
            # Create memory directory if it doesn't exist
            self.memory_path.mkdir(parents=True, exist_ok=True)
            
            # Load existing memory if available
            if self.memory_file.exists():
                self._load_memory()
                logger.info(f"Loaded existing memory with {len(self.episodic_memory)} interactions")
            else:
                logger.info("Starting with fresh memory")
            
            self.initialized = True
            logger.info("Memory system initialized")
            
        except Exception as e:
            logger.error(f"Error initializing memory: {e}")
            self.initialized = False
    
    def _load_memory(self):
        """Load memory from file"""
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.episodic_memory = data.get("episodic", [])
                self.semantic_memory = data.get("semantic", {})
        except Exception as e:
            logger.error(f"Error loading memory: {e}")
            self.episodic_memory = []
            self.semantic_memory = {}
    
    def _save_memory(self):
        """Save memory to file"""
        try:
            data = {
                "episodic": self.episodic_memory,
                "semantic": self.semantic_memory,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def store_interaction(self, interaction: Dict[str, Any]):
        """Store an interaction in episodic memory"""
        try:
            # Add timestamp if not present
            if "timestamp" not in interaction:
                interaction["timestamp"] = datetime.now().isoformat()
            
            # Add to episodic memory
            self.episodic_memory.append(interaction)
            
            # Keep only last 1000 interactions to prevent memory bloat
            if len(self.episodic_memory) > 1000:
                self.episodic_memory = self.episodic_memory[-1000:]
            
            # Extract semantic information
            self._extract_semantic_info(interaction)
            
            # Save to disk periodically (every 10 interactions)
            if len(self.episodic_memory) % 10 == 0:
                self._save_memory()
                
        except Exception as e:
            logger.error(f"Error storing interaction: {e}")
    
    def _extract_semantic_info(self, interaction: Dict[str, Any]):
        """Extract semantic information from interaction"""
        try:
            message = interaction.get("message", "")
            interaction_type = interaction.get("type", "")
            
            # Extract key topics and concepts
            topics = self._extract_topics(message)
            
            # Store in semantic memory
            for topic in topics:
                if topic not in self.semantic_memory:
                    self.semantic_memory[topic] = {
                        "count": 0,
                        "first_seen": interaction["timestamp"],
                        "last_seen": interaction["timestamp"],
                        "interactions": []
                    }
                
                self.semantic_memory[topic]["count"] += 1
                self.semantic_memory[topic]["last_seen"] = interaction["timestamp"]
                self.semantic_memory[topic]["interactions"].append({
                    "timestamp": interaction["timestamp"],
                    "type": interaction_type,
                    "session_id": interaction.get("session_id", "")
                })
                
        except Exception as e:
            logger.error(f"Error extracting semantic info: {e}")
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text (basic implementation)"""
        # Basic topic extraction - in future versions this will use NLP
        topics = []
        
        # Common topics/keywords
        common_topics = [
            "code", "programming", "python", "javascript", "html", "css",
            "file", "web", "search", "api", "database", "server",
            "ai", "machine learning", "data", "analysis", "help", "question"
        ]
        
        text_lower = text.lower()
        for topic in common_topics:
            if topic in text_lower:
                topics.append(topic)
        
        return topics
    
    def retrieve_relevant_memory(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant memories based on query"""
        try:
            query_topics = self._extract_topics(query)
            relevant_memories = []
            
            # Search through episodic memory
            for memory in reversed(self.episodic_memory):
                memory_topics = self._extract_topics(memory.get("message", ""))
                
                # Check for topic overlap
                if any(topic in memory_topics for topic in query_topics):
                    relevant_memories.append(memory)
                    
                    if len(relevant_memories) >= limit:
                        break
            
            return relevant_memories
            
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}")
            return []
    
    def get_conversation_context(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation context for a specific session"""
        try:
            session_memories = [
                memory for memory in self.episodic_memory
                if memory.get("session_id") == session_id
            ]
            
            return session_memories[-limit:]
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return []
    
    def get_summary(self) -> Dict[str, Any]:
        """Get memory system summary"""
        try:
            return {
                "episodic_count": len(self.episodic_memory),
                "semantic_topics": len(self.semantic_memory),
                "memory_file_size": self.memory_file.stat().st_size if self.memory_file.exists() else 0,
                "initialized": self.initialized,
                "top_topics": self._get_top_topics(5)
            }
        except Exception as e:
            logger.error(f"Error getting memory summary: {e}")
            return {
                "episodic_count": 0,
                "semantic_topics": 0,
                "memory_file_size": 0,
                "initialized": self.initialized,
                "top_topics": []
            }
    
    def _get_top_topics(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top topics by frequency"""
        try:
            topics = []
            for topic, info in self.semantic_memory.items():
                topics.append({
                    "topic": topic,
                    "count": info["count"],
                    "last_seen": info["last_seen"]
                })
            
            # Sort by count (descending)
            topics.sort(key=lambda x: x["count"], reverse=True)
            return topics[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top topics: {e}")
            return []
    
    def clear_memory(self):
        """Clear all memory"""
        try:
            self.episodic_memory = []
            self.semantic_memory = {}
            
            if self.memory_file.exists():
                self.memory_file.unlink()
            
            logger.info("Memory cleared")
            
        except Exception as e:
            logger.error(f"Error clearing memory: {e}")
    
    def export_memory(self, file_path: str):
        """Export memory to file"""
        try:
            data = {
                "episodic": self.episodic_memory,
                "semantic": self.semantic_memory,
                "exported_at": datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Memory exported to {file_path}")
            
        except Exception as e:
            logger.error(f"Error exporting memory: {e}")
    
    def import_memory(self, file_path: str):
        """Import memory from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.episodic_memory = data.get("episodic", [])
            self.semantic_memory = data.get("semantic", {})
            
            self._save_memory()
            logger.info(f"Memory imported from {file_path}")
            
        except Exception as e:
            logger.error(f"Error importing memory: {e}")

    def add_episode(self, user_id, message, response):
        """Add an episode to memory (for compatibility with tests)"""
        return self.save_episode(user_id, message, response)

    def get_episodes(self, user_id, limit=10):
        """Get episodes from memory (for compatibility with tests)"""
        return self.load_episodes(user_id, limit=limit)

# Global memory manager instance
_memory_manager = None

def get_memory_manager() -> MemoryManager:
    """Get global memory manager instance"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager 