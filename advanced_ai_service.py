import json
import os
import asyncio
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ai_services import ai_services
from memory_service import memory_service

class AdvancedAIService:
    """Multi-modal AI with personalized assistants and advanced context awareness"""
    
    def __init__(self):
        self.ai_personalities = self.load_ai_personalities()
        self.user_contexts = {}
        self.conversation_threads = {}
        self.automation_tasks = {}
        
    def load_ai_personalities(self) -> Dict[str, Dict[str, Any]]:
        """Load different AI personality profiles"""
        return {
            "professional": {
                "name": "Professor Alex",
                "description": "Formal, academic, detailed explanations",
                "prompt_style": "Respond in a professional, academic tone with detailed explanations and proper citations where applicable.",
                "specialties": ["business", "research", "analysis", "formal writing"]
            },
            "casual": {
                "name": "Buddy",
                "description": "Friendly, relaxed, conversational",
                "prompt_style": "Respond in a casual, friendly tone like talking to a close friend. Use everyday language and be relatable.",
                "specialties": ["general chat", "advice", "entertainment", "casual help"]
            },
            "creative": {
                "name": "Aria",
                "description": "Artistic, imaginative, expressive",
                "prompt_style": "Respond with creativity and imagination. Use vivid language, metaphors, and artistic expression.",
                "specialties": ["writing", "art", "music", "creative projects", "brainstorming"]
            },
            "technical": {
                "name": "CodeMaster",
                "description": "Precise, logical, problem-solving focused",
                "prompt_style": "Respond with technical precision, logical reasoning, and step-by-step problem-solving approaches.",
                "specialties": ["programming", "debugging", "technical analysis", "system design"]
            },
            "educational": {
                "name": "Tutor Sam",
                "description": "Patient, encouraging, learning-focused",
                "prompt_style": "Respond as a patient tutor who breaks down complex topics into understandable steps and encourages learning.",
                "specialties": ["teaching", "explanations", "study help", "skill development"]
            },
            "empathetic": {
                "name": "Luna",
                "description": "Understanding, supportive, emotionally aware",
                "prompt_style": "Respond with empathy and emotional intelligence. Be supportive, understanding, and emotionally aware.",
                "specialties": ["counseling", "emotional support", "life advice", "mental health"]
            }
        }
    
    def set_user_personality(self, user_id: str, personality: str) -> Dict[str, Any]:
        """Set AI personality for a user"""
        if personality not in self.ai_personalities:
            return {"error": f"Personality '{personality}' not found"}
        
        # Store in memory service
        memory_service.store_user_preference(user_id, "ai_personality", personality)
        
        selected = self.ai_personalities[personality]
        return {
            "success": True,
            "personality": personality,
            "name": selected["name"],
            "description": selected["description"],
            "specialties": selected["specialties"]
        }
    
    def get_user_personality(self, user_id: str) -> str:
        """Get user's preferred AI personality"""
        preference = memory_service.get_user_preference(user_id, "ai_personality")
        return preference if preference else "casual"
    
    def chat_with_personality(self, user_id: str, message: str, context: str = None) -> str:
        """Chat using user's preferred AI personality"""
        personality_key = self.get_user_personality(user_id)
        personality = self.ai_personalities[personality_key]
        
        # Get conversation context
        user_memory = memory_service.get_user_context(user_id)
        conversation_history = self.get_recent_conversation(user_id)
        
        # Build enhanced prompt
        enhanced_prompt = f"{personality['prompt_style']}\n\n"
        
        if user_memory:
            enhanced_prompt += f"User context: {user_memory.get('summary', '')}\n"
            enhanced_prompt += f"User preferences: {user_memory.get('preferences', {})}\n"
        
        if conversation_history:
            enhanced_prompt += f"Recent conversation: {conversation_history}\n"
        
        if context:
            enhanced_prompt += f"Current context: {context}\n"
        
        enhanced_prompt += f"\nUser message: {message}\n\nRespond as {personality['name']} focusing on: {', '.join(personality['specialties'])}"
        
        # Store conversation thread
        self.store_conversation_turn(user_id, message, "user")
        
        response = ai_services.chat_with_ai(enhanced_prompt, f"personality_{personality_key}")
        
        # Store AI response
        self.store_conversation_turn(user_id, response, "assistant")
        
        return response
    
    def store_conversation_turn(self, user_id: str, message: str, role: str):
        """Store conversation turn for context"""
        if user_id not in self.conversation_threads:
            self.conversation_threads[user_id] = []
        
        self.conversation_threads[user_id].append({
            "role": role,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 20 turns
        if len(self.conversation_threads[user_id]) > 20:
            self.conversation_threads[user_id] = self.conversation_threads[user_id][-20:]
    
    def get_recent_conversation(self, user_id: str, turns: int = 6) -> str:
        """Get recent conversation turns for context"""
        if user_id not in self.conversation_threads:
            return ""
        
        recent = self.conversation_threads[user_id][-turns:]
        conversation = ""
        for turn in recent:
            role_prefix = "User" if turn["role"] == "user" else "Assistant"
            conversation += f"{role_prefix}: {turn['message']}\n"
        
        return conversation
    
    def analyze_document(self, file_path: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Advanced document analysis and processing"""
        try:
            if not os.path.exists(file_path):
                return {"error": "File not found"}
            
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                return self._analyze_pdf(file_path, analysis_type)
            elif file_ext in ['.txt', '.md', '.py', '.js', '.html', '.css']:
                return self._analyze_text_file(file_path, analysis_type)
            elif file_ext in ['.docx', '.doc']:
                return self._analyze_word_document(file_path, analysis_type)
            else:
                return {"error": f"Unsupported file type: {file_ext}"}
                
        except Exception as e:
            return {"error": f"Document analysis failed: {str(e)}"}
    
    def _analyze_text_file(self, file_path: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze text-based files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if len(content) > 10000:
                content = content[:10000] + "... [content truncated]"
            
            analysis_prompt = f"""Analyze this document with {analysis_type} analysis:

{content}

Provide:
1. Document summary and main points
2. Key topics and themes
3. Writing style and tone analysis
4. Important insights or findings
5. Structure and organization assessment
6. Recommendations or suggestions for improvement
7. Word count and readability assessment"""
            
            analysis = ai_services.chat_with_ai(analysis_prompt, "document_analysis")
            
            return {
                "file_type": "text",
                "analysis_type": analysis_type,
                "word_count": len(content.split()),
                "character_count": len(content),
                "analysis": analysis,
                "file_path": file_path
            }
            
        except Exception as e:
            return {"error": f"Text file analysis failed: {str(e)}"}
    
    def _analyze_pdf(self, file_path: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze PDF documents (simplified version)"""
        # For now, return a placeholder since PDF parsing requires additional libraries
        return {
            "file_type": "pdf",
            "analysis_type": analysis_type,
            "status": "PDF analysis requires additional setup",
            "suggestion": "Please convert PDF to text format for analysis",
            "file_path": file_path
        }
    
    def _analyze_word_document(self, file_path: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze Word documents (simplified version)"""
        return {
            "file_type": "word",
            "analysis_type": analysis_type,
            "status": "Word document analysis requires additional setup",
            "suggestion": "Please save as .txt format for analysis",
            "file_path": file_path
        }
    
    def generate_code(self, language: str, description: str, complexity: str = "intermediate") -> Dict[str, Any]:
        """Advanced code generation with multiple languages"""
        try:
            code_prompt = f"""Generate {complexity} level {language} code for this requirement:

{description}

Provide:
1. Complete, working code with proper syntax
2. Code comments explaining key sections
3. Error handling where appropriate
4. Usage examples
5. Dependencies or imports needed
6. Best practices followed
7. Alternative approaches if applicable

Make the code production-ready and well-documented."""
            
            code_response = ai_services.chat_with_ai(code_prompt, "code_generation")
            
            # Extract code blocks and explanations
            result = {
                "language": language,
                "complexity": complexity,
                "description": description,
                "generated_code": code_response,
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Code generation failed: {str(e)}"}
    
    def debug_code(self, code: str, language: str, error_message: str = None) -> Dict[str, Any]:
        """Advanced code debugging and optimization"""
        try:
            debug_prompt = f"""Debug and optimize this {language} code:

CODE:
```{language}
{code}
```

ERROR MESSAGE (if any):
{error_message if error_message else "No specific error provided"}

Provide:
1. Identified issues and bugs
2. Corrected code with fixes
3. Explanation of what was wrong
4. Performance optimization suggestions
5. Code quality improvements
6. Security considerations
7. Testing recommendations"""
            
            debug_response = ai_services.chat_with_ai(debug_prompt, "code_debugging")
            
            return {
                "language": language,
                "original_code": code,
                "error_message": error_message,
                "debug_analysis": debug_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Code debugging failed: {str(e)}"}
    
    def create_automation_task(self, user_id: str, task_name: str, schedule: str, action: str) -> Dict[str, Any]:
        """Create automated tasks and reminders"""
        try:
            task_id = f"auto_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            task = {
                "id": task_id,
                "user_id": user_id,
                "name": task_name,
                "schedule": schedule,
                "action": action,
                "created": datetime.now().isoformat(),
                "status": "active",
                "executions": []
            }
            
            self.automation_tasks[task_id] = task
            
            return {
                "success": True,
                "task_id": task_id,
                "task": task
            }
            
        except Exception as e:
            return {"error": f"Automation task creation failed: {str(e)}"}
    
    def process_automation_tasks(self):
        """Process pending automation tasks"""
        current_time = datetime.now()
        
        for task_id, task in self.automation_tasks.items():
            if task["status"] != "active":
                continue
            
            # Simple schedule processing (can be enhanced with cron-like syntax)
            try:
                if self._should_execute_task(task, current_time):
                    self._execute_automation_task(task)
            except Exception as e:
                print(f"Automation task execution failed: {e}")
    
    def _should_execute_task(self, task: Dict, current_time: datetime) -> bool:
        """Check if task should be executed now"""
        # Simplified scheduling logic
        schedule = task["schedule"].lower()
        
        if "daily" in schedule:
            # Check if task was executed today
            today = current_time.date().isoformat()
            recent_executions = [exec for exec in task["executions"] if exec["date"] == today]
            return len(recent_executions) == 0
        
        return False
    
    def _execute_automation_task(self, task: Dict):
        """Execute an automation task"""
        execution = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().date().isoformat(),
            "status": "completed"
        }
        
        task["executions"].append(execution)
        
        # Task execution logic would go here
        print(f"Executed automation task: {task['name']}")
    
    def get_user_automation_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all automation tasks for a user"""
        user_tasks = [task for task in self.automation_tasks.values() if task["user_id"] == user_id]
        return user_tasks
    
    def get_personality_options(self) -> Dict[str, Dict[str, Any]]:
        """Get all available AI personalities"""
        return self.ai_personalities

# Global instance
advanced_ai_service = AdvancedAIService()