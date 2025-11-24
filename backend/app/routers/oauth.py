from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import get_current_active_user
from app.models import User, PlatformConnection
from app.schemas import PlatformConnectionCreate, PlatformConnectionResponse

from typing import List
import httpx
import json
from datetime import datetime, timedelta
import os

router = APIRouter(tags=["oauth"])

@router.get("/debug")
async def debug_oauth_config():
    """Debug endpoint to check OAuth configuration"""
    config = get_oauth_config()
    debug_info = {}
    for platform, platform_config in config.items():
        debug_info[platform] = {
            "client_id": platform_config["client_id"],
            "client_secret": "***" if platform_config["client_secret"] else None,
            "has_credentials": bool(platform_config["client_id"] and platform_config["client_secret"]),
            "auth_url": platform_config["auth_url"],
            "token_url": platform_config["token_url"],
            "redirect_uri": platform_config["redirect_uri"],
            "scopes": platform_config["scopes"]
        }
    return debug_info

@router.get("/debug/connections")
async def debug_connections(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Debug endpoint to check stored connections"""
    connections = db.query(PlatformConnection).filter(
        PlatformConnection.user_id == current_user.id
    ).all()
    
    debug_info = {
        "user_id": current_user.id,
        "user_email": current_user.email,
        "connections": []
    }
    
    for conn in connections:
        debug_info["connections"].append({
            "id": conn.id,
            "platform": conn.platform,
            "platform_user_id": conn.platform_user_id,
            "platform_username": conn.platform_username,
            "is_active": conn.is_active,
            "has_access_token": bool(conn.access_token),
            "has_refresh_token": bool(conn.refresh_token),
            "expires_at": conn.expires_at.isoformat() if conn.expires_at else None,
            "created_at": conn.created_at.isoformat(),
            "updated_at": conn.updated_at.isoformat() if conn.updated_at else None
        })
    
    return debug_info

@router.get("/test-linkedin-connect")
async def test_linkedin_connect():
    """Test LinkedIn OAuth connection URL generation"""
    config = get_oauth_config()
    linkedin_config = config.get("linkedin")
    
    if not linkedin_config or not linkedin_config["client_id"]:
        return {"error": "LinkedIn OAuth not configured"}
    
    # Generate a test OAuth URL
    auth_url = (
        f"{linkedin_config['auth_url']}"
        f"?response_type=code"
        f"&client_id={linkedin_config['client_id']}"
        f"&redirect_uri={linkedin_config['redirect_uri']}"
        f"&state=test_user:test_state"
        f"&scope={'+'.join(linkedin_config['scopes'])}"
    )
    
    return {
        "auth_url": auth_url,
        "config": {
            "client_id": linkedin_config["client_id"],
            "redirect_uri": linkedin_config["redirect_uri"],
            "scopes": linkedin_config["scopes"]
        }
    }

@router.get("/test-linkedin")
async def test_linkedin_oauth():
    """Test LinkedIn OAuth without authentication (for debugging)"""
    try:
        config = get_oauth_config()
        linkedin_config = config.get('linkedin')
        
        if not linkedin_config:
            return {"error": "LinkedIn configuration not found"}
        
        if not linkedin_config["client_id"] or not linkedin_config["client_secret"]:
            return {"error": "LinkedIn credentials missing"}
        
        # Generate a test OAuth URL
        import secrets
        state = secrets.token_urlsafe(32)
        
        auth_params = {
            "client_id": linkedin_config["client_id"],
            "redirect_uri": linkedin_config["redirect_uri"],
            "scope": " ".join(linkedin_config["scopes"]),
            "response_type": "code",
            "state": state
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in auth_params.items()])
        auth_url = f"{linkedin_config['auth_url']}?{query_string}"
        
        return {
            "status": "success",
            "auth_url": auth_url,
            "config": {
                "client_id": linkedin_config["client_id"],
                "redirect_uri": linkedin_config["redirect_uri"],
                "scopes": linkedin_config["scopes"]
            }
        }
        
    except Exception as e:
        return {"error": str(e)}

@router.post("/test-linkedin-callback")
async def test_linkedin_callback(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Test LinkedIn OAuth callback simulation"""
    try:
        # Simulate a successful LinkedIn OAuth callback
        test_token_data = {
            "access_token": "test_access_token_123",
            "refresh_token": "test_refresh_token_123",
            "expires_in": 3600
        }
        
        test_user_info = {
            "id": "test_linkedin_user_123",
            "username": "Test LinkedIn User"
        }
        
        # Store the test connection
        connection = PlatformConnection(
            user_id=user_id,
            platform="linkedin",
            access_token=test_token_data["access_token"],
            refresh_token=test_token_data.get("refresh_token"),
            expires_at=datetime.utcnow() + timedelta(seconds=test_token_data.get("expires_in", 3600)),
            platform_user_id=test_user_info.get("id"),
            platform_username=test_user_info.get("username"),
            is_active=True
        )
        
        db.add(connection)
        db.commit()
        db.refresh(connection)
        
        return {
            "message": "Test LinkedIn connection created successfully",
            "connection_id": connection.id,
            "platform": connection.platform,
            "username": connection.platform_username,
            "is_active": connection.is_active
        }
        
    except Exception as e:
        print(f"ERROR in test_linkedin_callback: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create test connection: {str(e)}"
        )

def get_oauth_config():
    """Get OAuth configuration with proper environment variable loading"""
    from dotenv import load_dotenv
    load_dotenv()
    
    return {
        "twitter": {
            "client_id": os.getenv("TWITTER_CLIENT_ID"),
            "client_secret": os.getenv("TWITTER_CLIENT_SECRET"),
            "auth_url": "https://twitter.com/i/oauth2/authorize",
            "token_url": "https://api.twitter.com/2/oauth2/token",
            "redirect_uri": "http://localhost:8000/oauth/twitter/callback",
            "scopes": ["tweet.read", "tweet.write", "users.read", "offline.access"]
        },
        "linkedin": {
            "client_id": os.getenv("LINKEDIN_CLIENT_ID"),
            "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET"),
            "auth_url": "https://www.linkedin.com/oauth/v2/authorization",
            "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
            "redirect_uri": "http://localhost:8000/oauth/linkedin/callback",
            "scopes": ["openid", "profile", "email", "w_member_social"]
        },
        "facebook": {
            "client_id": os.getenv("FACEBOOK_APP_ID"),
            "client_secret": os.getenv("FACEBOOK_APP_SECRET"),
            "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
            "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
            "redirect_uri": "http://localhost:8000/oauth/facebook/callback",
            "scopes": ["pages_manage_posts", "pages_read_engagement", "pages_show_list"]
        },
        "instagram": {
            "client_id": os.getenv("INSTAGRAM_APP_ID"),
            "client_secret": os.getenv("INSTAGRAM_APP_SECRET"),
            "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
            "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
            "redirect_uri": "http://localhost:8000/oauth/instagram/callback",
            "scopes": ["instagram_basic", "instagram_content_publish", "pages_show_list"]
        }
    }

@router.get("/{platform}/connect")
async def initiate_oauth(
    platform: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Initiate OAuth flow for a specific platform"""
    try:
        print(f"DEBUG: OAuth connect request for platform: {platform}")
        print(f"DEBUG: Current user: {current_user.id} - {current_user.email}")
        
        oauth_config = get_oauth_config()
        if platform not in oauth_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platform: {platform}"
            )
        
        config = oauth_config[platform]
        print(f"DEBUG: Platform config: {config}")
        
        # Validate that we have the required credentials
        if not config["client_id"] or not config["client_secret"]:
            print(f"ERROR: Missing credentials for {platform}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OAuth credentials not configured for {platform}. Please check your environment variables."
            )
        
        print(f"DEBUG: Initiating OAuth for {platform} with client_id: {config['client_id']}")
        
        # Check if user already has an active connection
        existing_connection = db.query(PlatformConnection).filter(
            PlatformConnection.user_id == current_user.id,
            PlatformConnection.platform == platform,
            PlatformConnection.is_active == True
        ).first()
        
        if existing_connection:
            print(f"DEBUG: User already has connection to {platform}")
            # If connection exists and is still valid, return success
            if existing_connection.expires_at and existing_connection.expires_at > datetime.utcnow():
                return {"message": f"Already connected to {platform}", "status": "connected"}
        
        # Generate OAuth state for security and store user info
        import secrets
        state = secrets.token_urlsafe(32)
        
        # Store state with user info (in production, use Redis or database)
        # For now, we'll encode user info in the state
        state_data = f"{current_user.id}:{state}"
        
        # Build OAuth URL
        auth_params = {
            "client_id": config["client_id"],
            "redirect_uri": config["redirect_uri"],
            "scope": " ".join(config["scopes"]),
            "response_type": "code",
            "state": state_data
        }
        
        if platform == "facebook" or platform == "instagram":
            auth_params["response_type"] = "code"
        
        # Build query string
        query_string = "&".join([f"{k}={v}" for k, v in auth_params.items()])
        auth_url = f"{config['auth_url']}?{query_string}"
        
        print(f"DEBUG: Generated OAuth URL: {auth_url}")
        print(f"DEBUG: OAuth flow initiated successfully for {platform}")
        
        return {"auth_url": auth_url, "state": state}
        
    except Exception as e:
        print(f"ERROR in initiate_oauth: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate OAuth flow: {str(e)}"
        )

@router.get("/{platform}/callback")
async def oauth_callback(
    platform: str,
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle OAuth callback from social media platforms"""
    print("=" * 80)
    print("🔗 OAUTH CALLBACK STARTED")
    print("=" * 80)
    print(f"📱 Platform: {platform}")
    print(f"🔑 Authorization code: {code[:20]}...")
    print(f"🔐 State: {state}")
    print(f"🌐 Request URL: {request.url}")
    print(f"📋 Query params: {dict(request.query_params)}")
    print("=" * 80)
    
    oauth_config = get_oauth_config()
    if platform not in oauth_config:
        print(f"ERROR: Unsupported platform: {platform}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported platform: {platform}"
        )
    
    config = oauth_config[platform]
    print(f"DEBUG: Platform config loaded: {config}")
    
    try:
        # Extract user ID from state (format: "user_id:random_state")
        if ":" not in state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state parameter"
            )
        
        user_id_str, random_state = state.split(":", 1)
        try:
            user_id = int(user_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID in state"
            )
        
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        print("🔄 STEP 1: TOKEN EXCHANGE")
        print("=" * 50)
        print(f"📱 Platform: {platform}")
        print(f"🔑 Code: {code[:20]}...")
        print(f"🌐 Token URL: {config['token_url']}")
        print(f"🔐 Client ID: {config['client_id']}")
        print(f"🔐 Client Secret: {'*' * len(config['client_secret']) if config['client_secret'] else 'MISSING'}")
        print("=" * 50)
        
        # Exchange authorization code for access token
        token_data = await exchange_code_for_token(platform, code, config)
        
        print("✅ TOKEN EXCHANGE SUCCESSFUL")
        print("=" * 50)
        print(f"🎫 Access Token: {token_data.get('access_token', 'MISSING')[:20]}...")
        print(f"🔄 Refresh Token: {token_data.get('refresh_token', 'MISSING')[:20] if token_data.get('refresh_token') else 'NONE'}...")
        print(f"⏰ Expires In: {token_data.get('expires_in', 'MISSING')} seconds")
        print("=" * 50)
        
        print("👤 STEP 2: USER INFO RETRIEVAL")
        print("=" * 50)
        print(f"📱 Platform: {platform}")
        print(f"🎫 Access Token: {token_data['access_token'][:20]}...")
        print("=" * 50)
        
        # Get user info from the platform
        user_info = await get_platform_user_info(platform, token_data["access_token"], token_data.get("id_token"))
        
        print("✅ USER INFO RETRIEVED")
        print("=" * 50)
        print(f"🆔 User ID: {user_info.get('id', 'MISSING')}")
        print(f"👤 Username: {user_info.get('username', 'MISSING')}")
        print(f"📋 Full User Info: {user_info}")
        print("=" * 50)
        
        print("💾 STEP 3: DATABASE OPERATIONS")
        print("=" * 50)
        print(f"👤 User ID: {user_id}")
        print(f"📱 Platform: {platform}")
        print("=" * 50)
        
        # Store or update the connection
        connection = db.query(PlatformConnection).filter(
            PlatformConnection.user_id == user_id,
            PlatformConnection.platform == platform
        ).first()
        
        if connection:
            print("🔄 UPDATING EXISTING CONNECTION")
            print("=" * 50)
            print(f"🆔 Connection ID: {connection.id}")
            print(f"📱 Platform: {connection.platform}")
            print(f"👤 User ID: {connection.user_id}")
            print("=" * 50)
            
            # Update existing connection
            connection.access_token = token_data["access_token"]
            connection.refresh_token = token_data.get("refresh_token")
            connection.expires_at = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
            connection.platform_user_id = user_info.get("id")
            connection.platform_username = user_info.get("username")
            connection.is_active = True
            
            print("✅ CONNECTION UPDATED")
            print("=" * 50)
            print(f"🎫 Access Token: {connection.access_token[:20]}...")
            print(f"🔄 Refresh Token: {connection.refresh_token[:20] if connection.refresh_token else 'NONE'}...")
            print(f"⏰ Expires At: {connection.expires_at}")
            print(f"🆔 Platform User ID: {connection.platform_user_id}")
            print(f"👤 Platform Username: {connection.platform_username}")
            print(f"✅ Is Active: {connection.is_active}")
            print("=" * 50)
        else:
            print("🆕 CREATING NEW CONNECTION")
            print("=" * 50)
            
            # Create new connection
            connection = PlatformConnection(
                user_id=user_id,
                platform=platform,
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                expires_at=datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600)),
                platform_user_id=user_info.get("id"),
                platform_username=user_info.get("username"),
                is_active=True
            )
            db.add(connection)
            
            print("✅ NEW CONNECTION CREATED")
            print("=" * 50)
            print(f"🎫 Access Token: {connection.access_token[:20]}...")
            print(f"🔄 Refresh Token: {connection.refresh_token[:20] if connection.refresh_token else 'NONE'}...")
            print(f"⏰ Expires At: {connection.expires_at}")
            print(f"🆔 Platform User ID: {connection.platform_user_id}")
            print(f"👤 Platform Username: {connection.platform_username}")
            print(f"✅ Is Active: {connection.is_active}")
            print("=" * 50)
        
        print("💾 COMMITTING TO DATABASE")
        print("=" * 50)
        db.commit()
        db.refresh(connection)
        print("✅ DATABASE COMMIT SUCCESSFUL")
        print("=" * 50)
        print(f"🆔 Final Connection ID: {connection.id}")
        print(f"📱 Final Platform: {connection.platform}")
        print(f"👤 Final Username: {connection.platform_username}")
        print(f"✅ Final Is Active: {connection.is_active}")
        print("=" * 50)
        
        print("🌐 STEP 4: REDIRECTING TO FRONTEND")
        print("=" * 50)
        redirect_url = f"http://localhost:3000/profile?connection=success&platform={platform}&username={connection.platform_username or 'LinkedIn User'}"
        print(f"🔗 Redirect URL: {redirect_url}")
        print("=" * 50)
        
        print("🎉 OAUTH CALLBACK COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"✅ Platform: {platform}")
        print(f"✅ User ID: {user_id}")
        print(f"✅ Connection ID: {connection.id}")
        print(f"✅ Username: {connection.platform_username}")
        print(f"✅ Is Active: {connection.is_active}")
        print("=" * 80)
        
        # Redirect to frontend with success
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        print("❌ OAUTH CALLBACK FAILED")
        print("=" * 80)
        print(f"🚨 Error: {str(e)}")
        print(f"📱 Platform: {platform}")
        print(f"🔑 Code: {code[:20] if code else 'MISSING'}...")
        print(f"🔐 State: {state}")
        print("=" * 80)
        print("📋 FULL TRACEBACK:")
        import traceback
        traceback.print_exc()
        print("=" * 80)
        
        # Redirect to frontend with error
        error_url = f"http://localhost:3000/profile?connection=error&platform={platform}&error={str(e)}"
        print(f"🔗 Error Redirect URL: {error_url}")
        print("=" * 80)
        
        return RedirectResponse(url=error_url)

async def exchange_code_for_token(platform: str, code: str, config: dict):
    """Exchange authorization code for access token"""
    print("🔄 TOKEN EXCHANGE FUNCTION STARTED")
    print("=" * 50)
    print(f"📱 Platform: {platform}")
    print(f"🔑 Code: {code[:20]}...")
    print(f"🌐 Token URL: {config['token_url']}")
    print(f"🔐 Client ID: {config['client_id']}")
    print(f"🔐 Client Secret: {'*' * len(config['client_secret']) if config['client_secret'] else 'MISSING'}")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        token_data = {
            "code": code,
            "redirect_uri": config["redirect_uri"],
            "grant_type": "authorization_code"
        }
        
        print("📋 TOKEN REQUEST DATA")
        print("=" * 50)
        print(f"🔑 Code: {token_data['code'][:20]}...")
        print(f"🌐 Redirect URI: {token_data['redirect_uri']}")
        print(f"📝 Grant Type: {token_data['grant_type']}")
        print("=" * 50)
        
        if platform == "twitter":
            # Twitter uses Basic Auth with client credentials
            import base64
            credentials = base64.b64encode(
                f"{config['client_id']}:{config['client_secret']}".encode()
            ).decode()
            
            headers = {"Authorization": f"Basic {credentials}"}
            response = await client.post(
                config["token_url"],
                data=token_data,
                headers=headers
            )
        elif platform == "linkedin":
            # LinkedIn OAuth 2.0 - requires specific format
            linkedin_data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": config["redirect_uri"],
                "client_id": config["client_id"],
                "client_secret": config["client_secret"]
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }
            
            print("🔗 LINKEDIN TOKEN EXCHANGE")
            print("=" * 50)
            print(f"🌐 Token URL: {config['token_url']}")
            print(f"📋 Request Data:")
            print(f"  🔑 Code: {linkedin_data['code'][:20]}...")
            print(f"  🌐 Redirect URI: {linkedin_data['redirect_uri']}")
            print(f"  📝 Grant Type: {linkedin_data['grant_type']}")
            print(f"  🔐 Client ID: {linkedin_data['client_id']}")
            print(f"  🔐 Client Secret: {'*' * len(linkedin_data['client_secret']) if linkedin_data['client_secret'] else 'MISSING'}")
            print(f"📋 Headers: {headers}")
            print("=" * 50)
            
            response = await client.post(config["token_url"], data=linkedin_data, headers=headers)
            
            print("📡 LINKEDIN TOKEN RESPONSE")
            print("=" * 50)
            print(f"📊 Status Code: {response.status_code}")
            print(f"📋 Response Headers: {dict(response.headers)}")
            print(f"📄 Response Body: {response.text}")
            print("=" * 50)
        else:
            # Facebook, Instagram use standard OAuth
            token_data.update({
                "client_id": config["client_id"],
                "client_secret": config["client_secret"]
            })
            response = await client.post(config["token_url"], data=token_data)
        
        print(f"DEBUG: Token exchange response status: {response.status_code}")
        print(f"DEBUG: Token exchange response headers: {dict(response.headers)}")
        print(f"DEBUG: Token exchange response body: {response.text}")
        
        if response.status_code != 200:
            print(f"ERROR: Token exchange failed with status {response.status_code}")
            print(f"ERROR: Response text: {response.text}")
            print(f"ERROR: Request URL: {config['token_url']}")
            print(f"ERROR: Request data: {token_data if platform != 'linkedin' else 'LinkedIn data (see above)'}")
            raise Exception(f"Token exchange failed: HTTP {response.status_code} - {response.text}")
        
        token_response = response.json()
        print(f"DEBUG: Token response parsed: {token_response}")
        return token_response

async def get_platform_user_info(platform: str, access_token: str, id_token: str = None):
    """Get user information from the platform"""
    print("👤 USER INFO RETRIEVAL FUNCTION STARTED")
    print("=" * 50)
    print(f"📱 Platform: {platform}")
    print(f"🎫 Access Token: {access_token[:20]}...")
    print(f"🆔 ID Token: {id_token[:20] if id_token else 'None'}...")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        if platform == "twitter":
            url = "https://api.twitter.com/2/users/me"
        elif platform == "linkedin":
            # For LinkedIn, try to use ID token first, then fallback to API call
            if id_token:
                try:
                    import base64
                    import json
                    
                    # Decode the ID token (JWT)
                    # Split the token and get the payload (middle part)
                    parts = id_token.split('.')
                    if len(parts) >= 2:
                        # Add padding if needed
                        payload = parts[1]
                        payload += '=' * (4 - len(payload) % 4)
                        
                        # Decode base64
                        decoded_payload = base64.urlsafe_b64decode(payload)
                        user_data = json.loads(decoded_payload)
                        
                        print("🔗 LINKEDIN ID TOKEN DECODED")
                        print("=" * 50)
                        print(f"📋 ID Token Data: {user_data}")
                        print(f"🆔 ID: {user_data.get('sub', 'MISSING')}")
                        print(f"👤 Name: {user_data.get('name', 'MISSING')}")
                        print(f"👤 First Name: {user_data.get('given_name', 'MISSING')}")
                        print(f"👤 Last Name: {user_data.get('family_name', 'MISSING')}")
                        print("=" * 50)
                        
                        first_name = user_data.get("given_name", "")
                        last_name = user_data.get("family_name", "")
                        full_name = f"{first_name} {last_name}".strip() or user_data.get("name", "LinkedIn User")
                        
                        result = {
                            "id": user_data["sub"],
                            "username": full_name
                        }
                        
                        print("✅ LINKEDIN USER INFO FROM ID TOKEN")
                        print("=" * 50)
                        print(f"🆔 Final ID: {result['id']}")
                        print(f"👤 Final Username: {result['username']}")
                        print("=" * 50)
                        
                        return result
                except Exception as e:
                    print(f"❌ Failed to decode ID token: {e}")
                    print("🔄 Falling back to API call...")
            
            # Fallback to API call if ID token fails
            url = "https://api.linkedin.com/v2/me?projection=(id,localizedFirstName,localizedLastName)"
        elif platform == "facebook":
            url = "https://graph.facebook.com/v18.0/me"
        elif platform == "instagram":
            url = "https://graph.facebook.com/v18.0/me/accounts"
        else:
            print("❌ UNSUPPORTED PLATFORM")
            return {"id": "unknown", "username": "unknown"}
        
        print("📡 USER INFO REQUEST")
        print("=" * 50)
        print(f"🌐 URL: {url}")
        print(f"📋 Headers: {headers}")
        print("=" * 50)
        
        response = await client.get(url, headers=headers)
        
        print("📡 USER INFO RESPONSE")
        print("=" * 50)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        print(f"📄 Response Body: {response.text}")
        print("=" * 50)
        
        if response.status_code != 200:
            print(f"❌ FAILED TO GET USER INFO: HTTP {response.status_code}")
            return {"id": "unknown", "username": "unknown"}
        
        data = response.json()
        print(f"✅ USER INFO DATA PARSED: {data}")
        print("=" * 50)
        
        # Extract user info based on platform
        if platform == "twitter":
            return {
                "id": data["data"]["id"],
                "username": data["data"]["username"]
            }
        elif platform == "linkedin":
            # Handle LinkedIn API v2 response format
            print("🔗 LINKEDIN USER INFO EXTRACTION")
            print("=" * 50)
            print(f"📋 Raw Data: {data}")
            print(f"🆔 ID: {data.get('id', 'MISSING')}")
            print(f"👤 First Name: {data.get('localizedFirstName', 'MISSING')}")
            print(f"👤 Last Name: {data.get('localizedLastName', 'MISSING')}")
            print("=" * 50)
            
            first_name = data.get("localizedFirstName", "")
            last_name = data.get("localizedLastName", "")
            full_name = f"{first_name} {last_name}".strip()
            
            result = {
                "id": data["id"],
                "username": full_name or "LinkedIn User"
            }
            
            print("✅ LINKEDIN USER INFO EXTRACTED")
            print("=" * 50)
            print(f"🆔 Final ID: {result['id']}")
            print(f"👤 Final Username: {result['username']}")
            print("=" * 50)
            
            return result
        elif platform == "facebook":
            return {
                "id": data["id"],
                "username": data.get("name", "Unknown")
            }
        elif platform == "instagram":
            # Instagram requires additional setup through Facebook
            return {
                "id": "instagram_user",
                "username": "instagram_user"
            }
        
        return {"id": "unknown", "username": "unknown"}

@router.get("/connections", response_model=List[PlatformConnectionResponse])
async def get_user_connections(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all platform connections for the current user"""
    connections = db.query(PlatformConnection).filter(
        PlatformConnection.user_id == current_user.id,
        PlatformConnection.is_active == True
    ).all()
    
    return connections

@router.delete("/connections/{platform}")
async def disconnect_platform(
    platform: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Disconnect a platform connection"""
    connection = db.query(PlatformConnection).filter(
        PlatformConnection.user_id == current_user.id,
        PlatformConnection.platform == platform,
        PlatformConnection.is_active == True
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active connection found for {platform}"
        )
    
    connection.is_active = False
    db.commit()
    
    return {"message": f"Successfully disconnected from {platform}"}
