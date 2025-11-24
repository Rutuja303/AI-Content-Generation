# AI Content Generator - Setup Guide

This guide will help you set up and run the AI Content Generator application locally.

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- PostgreSQL (if running locally without Docker)

## Required API Keys

Before running the application, you'll need to obtain the following API keys:

### 1. OpenAI API Key
- Visit [OpenAI Platform](https://platform.openai.com/)
- Create an account and add billing information
- Generate an API key
- Add to `.env` file as `OPENAI_API_KEY`

### 2. Social Media Platform APIs

#### Twitter API (X)
- Visit [Twitter Developer Portal](https://developer.twitter.com/)
- Create a new app
- Get API Key, API Secret, Access Token, and Access Token Secret
- Add to `.env` file

#### Meta (Facebook/Instagram)
- Visit [Meta for Developers](https://developers.facebook.com/)
- Create a new app
- Get App ID and App Secret
- Add to `.env` file

#### LinkedIn API
- Visit [LinkedIn Developer Portal](https://developer.linkedin.com/)
- Create a new app
- Get Client ID and Client Secret
- Add to `.env` file

#### SendGrid (Email)
- Visit [SendGrid](https://sendgrid.com/)
- Create an account
- Generate an API key
- Add to `.env` file

## Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Marketing
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Local Development Setup

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp ../env.example .env
   # Edit .env with your API keys
   ```

5. **Run the backend**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp ../env.example .env
   # Edit .env with your API keys
   ```

4. **Run the frontend**
   ```bash
   npm start
   ```

## Database Setup

### With Docker (Recommended)
The database will be automatically set up when you run `docker-compose up -d`.

### Local PostgreSQL
1. Install PostgreSQL
2. Create a database:
   ```sql
   CREATE DATABASE content_generator;
   ```
3. Update the `DATABASE_URL` in your `.env` file

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/content_generator
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=content_generator

# Backend Configuration
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4

# OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret

# Twitter API (X) Configuration
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret
TWITTER_ACCESS_TOKEN=your-twitter-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-twitter-access-token-secret

# Meta (Facebook/Instagram) Configuration
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
INSTAGRAM_ACCESS_TOKEN=your-instagram-access-token

# Email Configuration (SendGrid)
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id
REACT_APP_LINKEDIN_CLIENT_ID=your-linkedin-client-id
```

## Usage

1. **Register/Login**: Create an account or sign in
2. **Generate Content**: 
   - Go to "Generate Content" page
   - Enter a prompt describing what you want to create
   - Select platforms (Twitter, Instagram, LinkedIn, Facebook, Email)
   - Click "Generate Content"
3. **Review and Edit**: 
   - Review the generated content
   - Edit if needed
   - Copy to clipboard or approve for publishing
4. **Publish**: 
   - Connect your social media accounts
   - Publish directly or schedule for later

## API Documentation

Once the backend is running, visit http://localhost:8000/docs to see the interactive API documentation.

## Troubleshooting

### Common Issues

1. **Database connection errors**
   - Ensure PostgreSQL is running
   - Check DATABASE_URL in .env file
   - Verify database exists

2. **API key errors**
   - Ensure all required API keys are set in .env
   - Check API key permissions and quotas

3. **CORS errors**
   - Verify BACKEND_CORS_ORIGINS includes your frontend URL
   - Check that frontend and backend ports match

4. **Docker issues**
   - Ensure Docker and Docker Compose are installed
   - Try rebuilding containers: `docker-compose down && docker-compose up --build`

### Logs

View logs for specific services:
```bash
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# Database logs
docker-compose logs postgres
```

## Development

### Backend Development
- The backend uses FastAPI with automatic reload
- API documentation is available at `/docs`
- Database migrations are handled automatically

### Frontend Development
- React with TypeScript
- TailwindCSS for styling
- Hot reload enabled

### Adding New Features
1. Backend: Add new routes in `app/routers/`
2. Frontend: Add new pages in `src/pages/`
3. Update API service in `src/services/api.ts`
4. Add navigation in `src/components/Layout.tsx`

## Deployment

### Production Considerations
1. Use environment-specific .env files
2. Set up proper SSL certificates
3. Configure production database
4. Set up monitoring and logging
5. Use proper secret management
6. Configure backup strategies

### Docker Production
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Run production stack
docker-compose -f docker-compose.prod.yml up -d
```

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check logs for error messages
4. Ensure all dependencies are properly installed
