# AI Content Generator - Multi-Platform Social Media Tool

An AI-powered content generator that creates optimized posts for multiple social media platforms from a single prompt.

## Features

- 🤖 AI-powered content generation using OpenAI GPT-4
- 📱 Multi-platform support (Twitter, Instagram, LinkedIn, Facebook, Email)
- 🔐 Secure authentication with JWT + OAuth2
- 📅 Post scheduling and publishing
- 📊 Basic analytics dashboard
- 🎨 Modern, responsive UI with TailwindCSS
- 🌙 Dark/Light mode with smooth transitions
- 👤 Comprehensive user profile management
- 🔗 Social media platform integration
- ⚙️ Advanced settings and preferences
- 📱 Mobile-first responsive design

## Tech Stack

- **Frontend**: React + TypeScript + TailwindCSS
- **Backend**: FastAPI (Python) + SQLAlchemy
- **Database**: PostgreSQL
- **AI**: OpenAI GPT-4 API
- **Authentication**: JWT + OAuth2
- **Deployment**: Docker

## Project Structure

```
Marketing/
├── frontend/                 # React frontend application
├── backend/                  # FastAPI backend application
├── database/                 # Database migrations and schema
├── docker-compose.yml        # Docker orchestration
├── .env.example             # Environment variables template
└── README.md                # This file
```

## Quick Start

1. **Clone and setup environment**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

2. **Start with Docker**:
   ```bash
   docker-compose up -d
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## User Experience Features

### 🎨 **Theme System**
- Toggle between light and dark modes
- Smooth color transitions
- Persistent theme preference
- Consistent styling across all components

### 👤 **Profile Management**
- Complete user profile information
- Secure password change functionality
- Social media platform connections
- Account settings and preferences

### 🔗 **Social Media Integration**
- Step-by-step connection guides for each platform
- Platform-specific instructions and requirements
- Connection status tracking
- Easy disconnect/reconnect functionality

### ⚙️ **Advanced Settings**
- **Notifications**: Email and push notification preferences
- **Privacy**: Profile and content visibility controls
- **Appearance**: Theme customization and preview
- **Data Management**: Export and account deletion options

### 📱 **Responsive Design**
- Mobile-first approach
- Optimized for all screen sizes
- Touch-friendly interface
- Consistent experience across devices

## Required API Keys

- **OpenAI API Key** (for content generation)
- **Twitter OAuth** (Client ID + Secret)
- **Meta OAuth** (Facebook/Instagram App ID + Secret)
- **LinkedIn OAuth** (Client ID + Secret)
- **SendGrid API** (for email campaigns)

## 🔗 OAuth Setup

The application now supports **real OAuth connections** to social media platforms:

- **Twitter (X)**: Full OAuth 2.0 flow with posting capabilities
- **LinkedIn**: Professional network integration
- **Facebook**: Page management and posting
- **Instagram**: Content publishing through Meta API
- **Email**: SendGrid integration for campaigns

### Quick OAuth Setup
1. Follow the [OAUTH_SETUP.md](OAUTH_SETUP.md) guide
2. Set up developer accounts on each platform
3. Configure OAuth apps with proper redirect URIs
4. Add credentials to your `.env` file
5. Test connections through the Profile page

## Detailed Setup Guide

For comprehensive setup instructions, API key configuration, and troubleshooting, see [SETUP.md](SETUP.md).

## Development Setup

See individual README files in `frontend/` and `backend/` directories for detailed development instructions.
