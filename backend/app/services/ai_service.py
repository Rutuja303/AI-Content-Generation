from openai import OpenAI
from typing import List, Dict, Optional, Union
from app.core.config import settings
import logging
import httpx
import base64
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.openai_model = settings.OPENAI_MODEL
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        
        # Google Gemini configuration
        self.gemini_api_key = getattr(settings, 'GEMINI_API_KEY', None)
        self.gemini_model = "gemini-2.0-flash-exp"
        
        # Groq configuration
        self.groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
        self.groq_model = "llama3-8b-8192"
        
        # Default to Gemini if available, otherwise OpenAI
        self.primary_provider = "gemini" if self.gemini_api_key else "openai"
    
    async def generate_platform_content(self, prompt: str, platforms: List[str], media_files: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Generate content for multiple platforms from a single prompt using LLM
        Supports media files (images/videos) for enhanced content generation
        """
        generated_content = {}
        
        # Analyze media files if provided
        media_analysis = ""
        if media_files:
            media_analysis = await self._analyze_media_files(media_files)
            if media_analysis:
                prompt = f"{prompt}\n\nMedia context: {media_analysis}"
        
        for platform in platforms:
            try:
                # Try primary provider first, then fallback
                content = await self._generate_with_provider(prompt, platform, self.primary_provider)
                if not content:
                    # Try fallback providers
                    for provider in ["openai", "groq", "gemini"]:
                        if provider != self.primary_provider:
                            content = await self._generate_with_provider(prompt, platform, provider)
                            if content:
                                break
                
                if not content:
                    logger.warning(f"All AI providers failed for {platform}, using fallback content")
                    content = self._get_fallback_content(prompt, platform)
                
                generated_content[platform] = content
                logger.info(f"Successfully generated content for {platform}: {content[:100]}...")
                
            except Exception as e:
                logger.error(f"Error generating content for {platform}: {str(e)}")
                # Fallback content if AI generation fails
                generated_content[platform] = self._get_fallback_content(prompt, platform)
        
        return generated_content
    
    async def _generate_with_provider(self, prompt: str, platform: str, provider: str) -> Optional[str]:
        """Generate content using specified provider"""
        try:
            if provider == "gemini" and self.gemini_api_key:
                return await self._generate_with_gemini(prompt, platform)
            elif provider == "openai" and self.openai_client:
                return await self._generate_with_openai(prompt, platform)
            elif provider == "groq" and self.groq_api_key:
                return await self._generate_with_groq(prompt, platform)
        except Exception as e:
            logger.error(f"Error with {provider} provider: {str(e)}")
        return None
    
    async def _generate_with_gemini(self, prompt: str, platform: str) -> str:
        """Generate content using Google Gemini"""
        system_prompt = self._get_system_prompt(platform)
        user_prompt = f"Create engaging content about: {prompt}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent",
                headers={"Content-Type": "application/json"},
                params={"key": self.gemini_api_key},
                json={
                    "contents": [{
                        "parts": [
                            {"text": f"{system_prompt}\n\n{user_prompt}"}
                        ]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 500
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            else:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return None
    
    async def _generate_with_openai(self, prompt: str, platform: str) -> str:
        """Generate content using OpenAI"""
        system_prompt = self._get_system_prompt(platform)
        user_prompt = f"Create engaging content about: {prompt}"
        
        response = self.openai_client.chat.completions.create(
            model=self.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    async def _generate_with_groq(self, prompt: str, platform: str) -> str:
        """Generate content using Groq"""
        system_prompt = self._get_system_prompt(platform)
        user_prompt = f"Create engaging content about: {prompt}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.groq_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            else:
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
                return None
    
    async def _analyze_media_files(self, media_files: List[str]) -> str:
        """Analyze uploaded media files and return description"""
        if not media_files or not self.gemini_api_key:
            return ""
        
        try:
            media_parts = []
            for file_path in media_files:
                if os.path.exists(file_path):
                    # Read and encode media file
                    with open(file_path, "rb") as f:
                        media_data = base64.b64encode(f.read()).decode()
                    
                    # Determine media type
                    file_ext = Path(file_path).suffix.lower()
                    if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                        mime_type = f"image/{file_ext[1:]}"
                    elif file_ext in ['.mp4', '.avi', '.mov', '.webm']:
                        mime_type = f"video/{file_ext[1:]}"
                    else:
                        continue
                    
                    media_parts.append({
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": media_data
                        }
                    })
            
            if not media_parts:
                return ""
            
            # Analyze media with Gemini
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent",
                    headers={"Content-Type": "application/json"},
                    params={"key": self.gemini_api_key},
                    json={
                        "contents": [{
                            "parts": [
                                {"text": "Analyze these media files and provide a detailed description of what you see. Focus on elements that would be relevant for creating social media content. Include details about the visual elements, mood, colors, and any text or objects visible."},
                                *media_parts
                            ]
                        }],
                        "generationConfig": {
                            "temperature": 0.3,
                            "maxOutputTokens": 300
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
                else:
                    logger.error(f"Media analysis error: {response.status_code} - {response.text}")
                    return ""
        
        except Exception as e:
            logger.error(f"Error analyzing media files: {str(e)}")
            return ""
    
    def _get_system_prompt(self, platform: str) -> str:
        """
        Get platform-specific system prompt for the LLM
        """
        prompts = {
            "twitter": """You are a Twitter content creator. Create ONE engaging, concise tweet (max 280 characters) that is:
            - Attention-grabbing and shareable
            - Include relevant hashtags (2-3 max)
            - Use emojis appropriately
            - Have a clear call-to-action when relevant
            - Match the conversational tone of Twitter
            - Return ONLY the final tweet text, no explanations or multiple options""",
            
            "instagram": """You are an Instagram content creator. Create ONE compelling Instagram caption that is:
            - Visually appealing and engaging
            - Include relevant hashtags (5-10 hashtags)
            - Use emojis to enhance the message
            - Have a storytelling element
            - Encourage engagement and comments
            - Match Instagram's visual-first approach
            - Return ONLY the final caption text, no explanations or multiple options""",
            
            "linkedin": """You are a LinkedIn content creator. Create ONE professional, thought-provoking post that is:
            - Business-focused and professional
            - Provide value and insights
            - Encourage professional discussion
            - Use a professional tone
            - Include relevant industry hashtags (2-3 max)
            - End with a question to encourage engagement
            - Return ONLY the final post text, no explanations or multiple options""",
            
            "facebook": """You are a Facebook content creator. Create ONE friendly, engaging post that is:
            - Conversational and approachable
            - Encourage community interaction
            - Use a warm, friendly tone
            - Include relevant hashtags (2-3 max)
            - Ask questions to drive engagement
            - Match Facebook's community-focused nature
            - Return ONLY the final post text, no explanations or multiple options""",
            
            "email": """You are an email marketing expert. Create ONE compelling email that includes:
            - A catchy subject line (max 50 characters)
            - Professional greeting and body
            - Clear value proposition
            - Strong call-to-action
            - Professional closing
            - Format: Subject: [subject line]\n\n[email body]
            - Return ONLY the final email content, no explanations or multiple options"""
        }
        
        return prompts.get(platform, "You are a content creator. Create engaging content that matches the platform's style and audience.")
    
    def _get_fallback_content(self, prompt: str, platform: str) -> str:
        """
        Provide fallback content if AI generation fails
        """
        # Create more meaningful content based on the prompt
        prompt_lower = prompt.lower()
        
        # Extract key topics from the prompt
        if "training" in prompt_lower:
            topic = "training and development"
        elif "marketing" in prompt_lower:
            topic = "marketing strategies"
        elif "ai" in prompt_lower or "artificial intelligence" in prompt_lower:
            topic = "artificial intelligence"
        elif "business" in prompt_lower:
            topic = "business growth"
        elif "technology" in prompt_lower:
            topic = "technology trends"
        else:
            topic = "professional development"
        
        fallback_templates = {
            "twitter": f"🚀 Excited to share insights about {topic}! This is a game-changer for professionals looking to stay ahead. What's your experience with {topic}? #professional #growth #innovation",
            
            "instagram": f"✨ Transform your approach to {topic}! 💡\n\nHere's what I've learned:\n• Stay curious and keep learning\n• Embrace new challenges\n• Connect with like-minded professionals\n\nWhat's your biggest challenge with {topic}? Share below! 👇\n\n#professional #growth #learning #success #motivation",
            
            "linkedin": f"Professional Insight: The Future of {topic.title()}\n\nAs professionals, we must continuously adapt and evolve our approach to {topic}. The landscape is changing rapidly, and those who stay ahead of the curve will thrive.\n\nKey considerations:\n• Understanding current trends\n• Developing relevant skills\n• Building strategic partnerships\n\nWhat strategies have you found most effective in {topic}? I'd love to hear your thoughts and experiences.\n\n#professional #growth #strategy #leadership",
            
            "facebook": f"Hey everyone! 👋\n\nI wanted to share some thoughts about {topic} that I've been thinking about lately. It's amazing how much the landscape has changed, and I believe we're just getting started!\n\nWhat I find most exciting is the opportunity for growth and innovation. Whether you're just starting out or you're a seasoned professional, there's always something new to learn.\n\nWhat's your take on {topic}? Have you noticed any interesting trends or changes? I'd love to hear your perspective!\n\n#professional #growth #community #learning",
            
            "email": f"Subject: Insights on {topic.title()}\n\nHi there,\n\nI hope this email finds you well. I wanted to share some thoughts about {topic} that I believe will be valuable for your professional journey.\n\nIn today's rapidly evolving landscape, staying informed about {topic} is more important than ever. The key is to remain adaptable and open to new approaches.\n\nI'd love to hear your thoughts on this topic and any insights you might have to share.\n\nBest regards,\n[Your Name]"
        }
        
        return fallback_templates.get(platform, f"Professional insight: {topic.title()}\n\nThis is an important topic that deserves attention and discussion. What are your thoughts on {topic}?")
    
    def improve_content(self, content: str, platform: str, feedback: str) -> str:
        """
        Improve existing content based on user feedback
        """
        try:
            if not self.client:
                return content  # Return original content if no API key
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are a social media expert. Improve this {platform} content based on the feedback."},
                    {"role": "user", "content": f"Original content: {content}\n\nFeedback: {feedback}\n\nPlease improve the content."}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error improving content: {str(e)}")
            return content  # Return original content if improvement fails
