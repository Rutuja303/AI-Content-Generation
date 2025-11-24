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
        
        # Default to OpenAI (GPT) as primary, then Gemini, then Groq
        if self.openai_client:
            self.primary_provider = "openai"
        elif self.gemini_api_key:
            self.primary_provider = "gemini"
        elif self.groq_api_key:
            self.primary_provider = "groq"
        else:
            self.primary_provider = "openai"  # Default even if no key (will fail gracefully)
    
    async def generate_platform_content(self, prompt: str, platforms: List[str], media_files: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Generate content for multiple platforms from a single user prompt using LLM
        Supports media files (images/videos) for enhanced content generation
        The content is generated based on the user's actual prompt, not generic templates
        """
        generated_content = {}
        
        # Analyze media files if provided
        media_analysis = ""
        if media_files:
            media_analysis = await self._analyze_media_files(media_files)
            logger.info(f"Media analysis completed: {media_analysis[:100]}...")
        
        # Use the user's prompt directly - don't modify it
        user_prompt = prompt.strip()
        
        for platform in platforms:
            try:
                # Try primary provider first (OpenAI/GPT), then fallback providers
                content = await self._generate_with_provider(user_prompt, platform, self.primary_provider, media_analysis)
                if not content:
                    # Try fallback providers in order: OpenAI -> Gemini -> Groq
                    fallback_providers = ["openai", "gemini", "groq"]
                    for provider in fallback_providers:
                        if provider != self.primary_provider:
                            content = await self._generate_with_provider(user_prompt, platform, provider, media_analysis)
                            if content:
                                logger.info(f"Successfully generated content for {platform} using {provider} fallback")
                                break
                
                if not content:
                    logger.warning(f"All AI providers failed for {platform}, using enhanced fallback content")
                    content = self._get_enhanced_fallback_content(user_prompt, platform, media_analysis)
                
                generated_content[platform] = content
                logger.info(f"Successfully generated content for {platform}: {content[:100]}...")
                
            except Exception as e:
                logger.error(f"Error generating content for {platform}: {str(e)}")
                # Enhanced fallback content if AI generation fails
                generated_content[platform] = self._get_enhanced_fallback_content(user_prompt, platform, media_analysis)
        
        return generated_content
    
    async def _generate_with_provider(self, prompt: str, platform: str, provider: str, media_context: str = "") -> Optional[str]:
        """Generate content using specified provider based on user's prompt"""
        try:
            if provider == "gemini" and self.gemini_api_key:
                return await self._generate_with_gemini(prompt, platform, media_context)
            elif provider == "openai" and self.openai_client:
                return await self._generate_with_openai(prompt, platform, media_context)
            elif provider == "groq" and self.groq_api_key:
                return await self._generate_with_groq(prompt, platform, media_context)
        except Exception as e:
            logger.error(f"Error with {provider} provider: {str(e)}")
        return None
    
    async def _generate_with_gemini(self, prompt: str, platform: str, media_context: str = "") -> str:
        """Generate content using Google Gemini based on user's prompt"""
        system_prompt = self._get_system_prompt(platform)
        
        # Build user prompt with media context if available
        user_prompt = prompt
        if media_context:
            user_prompt = f"{prompt}\n\nMedia context: {media_context}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent",
                headers={"Content-Type": "application/json"},
                params={"key": self.gemini_api_key},
                json={
                    "contents": [{
                        "parts": [
                            {"text": f"{system_prompt}\n\nUser's request: {user_prompt}"}
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
    
    async def _generate_with_openai(self, prompt: str, platform: str, media_context: str = "") -> str:
        """Generate content using OpenAI based on user's prompt"""
        system_prompt = self._get_system_prompt(platform)
        
        # Build user prompt with media context if available
        user_prompt = prompt
        if media_context:
            user_prompt = f"{prompt}\n\nMedia context: {media_context}"
        
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
    
    async def _generate_with_groq(self, prompt: str, platform: str, media_context: str = "") -> str:
        """Generate content using Groq based on user's prompt"""
        system_prompt = self._get_system_prompt(platform)
        
        # Build user prompt with media context if available
        user_prompt = prompt
        if media_context:
            user_prompt = f"{prompt}\n\nMedia context: {media_context}"
        
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
        """Analyze uploaded media files and return detailed description for content generation"""
        if not media_files:
            return ""
        
        # Try Gemini first (best for vision), then OpenAI if available
        if self.gemini_api_key:
            return await self._analyze_media_with_gemini(media_files)
        elif self.openai_client:
            return await self._analyze_media_with_openai(media_files)
        else:
            logger.warning("No AI provider available for media analysis")
            return ""
    
    async def _analyze_media_with_gemini(self, media_files: List[str]) -> str:
        """Analyze media files using Gemini Vision"""
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
                        mime_type = f"image/{file_ext[1:] if file_ext[1:] != 'jpg' else 'jpeg'}"
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
            
            # Analyze media with Gemini - focus on content creation context
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent",
                    headers={"Content-Type": "application/json"},
                    params={"key": self.gemini_api_key},
                    json={
                        "contents": [{
                            "parts": [
                                {"text": "Analyze these media files in detail. Describe what you see including: visual elements, colors, mood, any text visible, objects, people, setting, and overall theme. This description will be used to create social media content that matches the media, so be specific and detailed."},
                                *media_parts
                            ]
                        }],
                        "generationConfig": {
                            "temperature": 0.3,
                            "maxOutputTokens": 500
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    analysis = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    logger.info(f"Media analysis completed: {analysis[:100]}...")
                    return analysis
                else:
                    logger.error(f"Media analysis error: {response.status_code} - {response.text}")
                    return ""
        
        except Exception as e:
            logger.error(f"Error analyzing media files with Gemini: {str(e)}")
            return ""
    
    async def _analyze_media_with_openai(self, media_files: List[str]) -> str:
        """Analyze media files using OpenAI Vision (if available)"""
        # OpenAI vision requires different handling - for now return basic info
        # This can be enhanced if OpenAI vision API is needed
        logger.info("OpenAI vision analysis not fully implemented, using file names")
        return f"Media files uploaded: {', '.join([Path(f).name for f in media_files])}"
    
    def _get_system_prompt(self, platform: str) -> str:
        """
        Get platform-specific system prompt for the LLM
        These prompts instruct the LLM to generate content based on the user's actual prompt
        """
        prompts = {
            "twitter": """You are a Twitter content creator. Based on the user's request below, create ONE engaging, concise tweet (max 280 characters) that:
            - Directly addresses what the user asked for
            - Is attention-grabbing and shareable
            - Includes relevant hashtags (2-3 max)
            - Uses emojis appropriately
            - Has a clear call-to-action when relevant
            - Matches the conversational tone of Twitter
            - Reflects the user's intent and message
            - Return ONLY the final tweet text, no explanations or multiple options""",
            
            "instagram": """You are an Instagram content creator. Based on the user's request below, create ONE compelling Instagram caption that:
            - Directly addresses what the user asked for
            - Is visually appealing and engaging
            - Includes relevant hashtags (5-10 hashtags)
            - Uses emojis to enhance the message
            - Has a storytelling element
            - Encourages engagement and comments
            - Matches Instagram's visual-first approach
            - Reflects the user's intent and message
            - Return ONLY the final caption text, no explanations or multiple options""",
            
            "linkedin": """You are a LinkedIn content creator. Based on the user's request below, create ONE professional, thought-provoking post that:
            - Directly addresses what the user asked for
            - Is business-focused and professional
            - Provides value and insights related to the user's topic
            - Encourages professional discussion
            - Uses a professional tone
            - Includes relevant industry hashtags (2-3 max)
            - Ends with a question to encourage engagement
            - Reflects the user's intent and message
            - Return ONLY the final post text, no explanations or multiple options""",
            
            "facebook": """You are a Facebook content creator. Based on the user's request below, create ONE friendly, engaging post that:
            - Directly addresses what the user asked for
            - Is conversational and approachable
            - Encourages community interaction
            - Uses a warm, friendly tone
            - Includes relevant hashtags (2-3 max)
            - Asks questions to drive engagement
            - Matches Facebook's community-focused nature
            - Reflects the user's intent and message
            - Return ONLY the final post text, no explanations or multiple options""",
            
            "email": """You are an email marketing expert. Based on the user's request below, create ONE compelling email that:
            - Directly addresses what the user asked for
            - Includes a catchy subject line (max 50 characters)
            - Has a professional greeting and body
            - Provides clear value proposition related to the user's topic
            - Has a strong call-to-action
            - Uses professional closing
            - Format: Subject: [subject line]\n\n[email body]
            - Reflects the user's intent and message
            - Return ONLY the final email content, no explanations or multiple options"""
        }
        
        return prompts.get(platform, "You are a content creator. Based on the user's request, create engaging content that matches the platform's style and audience while directly addressing what the user asked for.")
    
    def _get_enhanced_fallback_content(self, prompt: str, platform: str, media_context: str = "") -> str:
        """
        Provide enhanced fallback content based on user's prompt if AI generation fails
        This creates platform-appropriate content based on the user's prompt, not just echoing it
        """
        user_message = prompt.strip()
        
        # Extract key information from prompt
        prompt_lower = user_message.lower()
        
        # Build context-aware content based on prompt keywords and platform
        if "training" in prompt_lower or "workshop" in prompt_lower:
            topic = "training session" if "training" in prompt_lower else "workshop"
            if platform == "twitter":
                return f"🎓 Excited to announce our upcoming {topic}! Join us for an engaging learning experience. {user_message} #training #learning #professional"
            elif platform == "instagram":
                return f"✨ Join us for an amazing {topic}! 🎓\n\n{user_message}\n\nDon't miss out on this opportunity to grow and learn! 📚\n\n#training #learning #growth #professional #workshop"
            elif platform == "linkedin":
                return f"Professional Development Opportunity: {user_message}\n\nWe're excited to offer this {topic} designed to help professionals enhance their skills and advance their careers.\n\nKey highlights:\n• Interactive learning experience\n• Practical insights and strategies\n• Networking opportunities\n\nInterested in joining? Let me know your thoughts!\n\n#professional #training #learning #development #career"
            elif platform == "facebook":
                return f"Hey everyone! 👋\n\nWe're thrilled to announce our upcoming {topic}! {user_message}\n\nThis is a great opportunity to learn, grow, and connect with others. Whether you're just starting out or looking to advance your skills, this {topic} has something for everyone.\n\nWhat questions do you have about the {topic}? Drop them in the comments! 💬\n\n#training #learning #community #growth"
            else:
                return f"Subject: Join Our {topic.title()}\n\nHi there,\n\n{user_message}\n\nWe'd love to have you join us for this valuable learning opportunity.\n\nBest regards"
        
        elif "launch" in prompt_lower or "product" in prompt_lower:
            if platform == "twitter":
                return f"🚀 Big announcement! {user_message} Stay tuned for more updates! #launch #innovation #excited"
            elif platform == "instagram":
                return f"🎉 Exciting news! ✨\n\n{user_message}\n\nWe can't wait to share this with you! Stay tuned for updates! 🔥\n\n#launch #newproduct #excited #innovation"
            elif platform == "linkedin":
                return f"Announcement: {user_message}\n\nWe're excited to share this development with our professional network. This represents an important milestone for us.\n\nWhat are your thoughts on this? We'd love to hear from you.\n\n#innovation #business #professional #announcement"
            elif platform == "facebook":
                return f"Hey everyone! 👋\n\nWe have some exciting news to share! {user_message}\n\nWe're so excited about this and can't wait to share more details with you all!\n\nWhat do you think? Let us know in the comments! 💬\n\n#announcement #excited #community"
            else:
                return f"Subject: Exciting Announcement\n\nHi there,\n\n{user_message}\n\nWe're thrilled to share this news with you!\n\nBest regards"
        
        else:
            # Generic but still platform-appropriate formatting
            if platform == "twitter":
                # Twitter: Keep it concise, add hashtags
                tweet = user_message[:240]  # Leave room for hashtags
                return f"{tweet} #content #socialmedia"
            elif platform == "instagram":
                # Instagram: Add engagement elements
                return f"{user_message}\n\n✨ Share your thoughts below! 👇\n\n#content #socialmedia #engagement #community"
            elif platform == "linkedin":
                # LinkedIn: Professional format
                return f"{user_message}\n\nI'd love to hear your thoughts and experiences on this topic. What are your insights?\n\n#professional #content #engagement #discussion"
            elif platform == "facebook":
                # Facebook: Community-focused
                return f"{user_message}\n\nWhat do you all think? I'd love to hear your thoughts and start a conversation! 💬\n\n#content #community #discussion"
            else:
                # Email: Professional format
                return f"Subject: {user_message[:50]}\n\nHi there,\n\n{user_message}\n\nI hope this message finds you well.\n\nBest regards"
    
    def _get_fallback_content(self, prompt: str, platform: str) -> str:
        """Legacy method - redirects to enhanced fallback"""
        return self._get_enhanced_fallback_content(prompt, platform)
    
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
