import tweepy
import facebook
from typing import Dict, Optional
from app.core.config import settings

class TwitterService:
    def __init__(self, access_token: str, access_token_secret: str):
        auth = tweepy.OAuthHandler(settings.TWITTER_API_KEY, settings.TWITTER_API_SECRET)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)
        self.client = tweepy.Client(
            consumer_key=settings.TWITTER_API_KEY,
            consumer_secret=settings.TWITTER_API_SECRET,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
    
    def publish_post(self, content: str) -> Dict:
        try:
            # Use Twitter API v2
            response = self.client.create_tweet(text=content)
            return {
                "success": True,
                "tweet_id": response.data["id"],
                "message": "Tweet published successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class FacebookService:
    def __init__(self, access_token: str):
        self.graph = facebook.GraphAPI(access_token=access_token, version="3.1")
    
    def publish_post(self, content: str, page_id: Optional[str] = None) -> Dict:
        try:
            if page_id:
                # Post to Facebook page
                response = self.graph.put_object(
                    parent_object=page_id,
                    connection_name="feed",
                    message=content
                )
            else:
                # Post to user's timeline
                response = self.graph.put_object(
                    parent_object="me",
                    connection_name="feed",
                    message=content
                )
            
            return {
                "success": True,
                "post_id": response["id"],
                "message": "Facebook post published successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class InstagramService:
    def __init__(self, access_token: str):
        self.access_token = access_token
        # Note: Instagram Basic Display API requires different approach
        # This is a simplified implementation
    
    def publish_post(self, content: str, image_url: Optional[str] = None) -> Dict:
        try:
            # Instagram API requires image for posts
            # This is a placeholder implementation
            return {
                "success": True,
                "message": "Instagram post would be published (requires image)",
                "note": "Instagram API requires image content for posts"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class LinkedInService:
    def __init__(self, access_token: str):
        self.access_token = access_token
        # LinkedIn API v2 implementation would go here
    
    def publish_post(self, content: str) -> Dict:
        try:
            # Placeholder for LinkedIn API implementation
            return {
                "success": True,
                "message": "LinkedIn post would be published",
                "note": "LinkedIn API integration requires additional setup"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class SocialMediaManager:
    def __init__(self):
        self.services = {}
    
    def get_service(self, platform: str, access_token: str, access_token_secret: str = None):
        if platform == "twitter":
            return TwitterService(access_token, access_token_secret)
        elif platform == "facebook":
            return FacebookService(access_token)
        elif platform == "instagram":
            return InstagramService(access_token)
        elif platform == "linkedin":
            return LinkedInService(access_token)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    def publish_content(self, platform: str, content: str, access_token: str, 
                       access_token_secret: str = None, **kwargs) -> Dict:
        try:
            service = self.get_service(platform, access_token, access_token_secret)
            return service.publish_post(content)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
