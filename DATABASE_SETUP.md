# 🗄️ **PostgreSQL Database Setup - Manual Configuration**

## 📋 **Database Configuration Files**

### **1. Docker Compose Configuration**
**File:** `docker-compose.yml`
```yaml
postgres:
  image: postgres:15
  container_name: content_generator_db
  environment:
    POSTGRES_USER: ${POSTGRES_USER:-user}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-password}
    POSTGRES_DB: ${POSTGRES_DB:-content_generator}
  volumes:
    - postgres_data:/var/lib/postgresql/data
  ports:
    - "5432:5432"
```

### **2. Backend Database Configuration**
**File:** `backend/app/database.py`
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine
engine = create_engine(settings.DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### **3. Settings Configuration**
**File:** `backend/app/core/config.py`
```python
class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/content_generator"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"
```

## 🗃️ **Database Schema**

### **Tables Created:**

#### **1. Users Table**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    role VARCHAR DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

#### **2. Prompts Table**
```sql
CREATE TABLE prompts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    prompt_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **3. Generated Posts Table**
```sql
CREATE TABLE generated_posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    prompt_id INTEGER REFERENCES prompts(id),
    platform VARCHAR NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

#### **4. Scheduled Posts Table**
```sql
CREATE TABLE scheduled_posts (
    id SERIAL PRIMARY KEY,
    generated_post_id INTEGER REFERENCES generated_posts(id) NOT NULL,
    platform VARCHAR NOT NULL,
    scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR DEFAULT 'scheduled',
    published_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **5. Platform Connections Table**
```sql
CREATE TABLE platform_connections (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    platform VARCHAR NOT NULL,
    access_token VARCHAR NOT NULL,
    refresh_token VARCHAR,
    expires_at TIMESTAMP WITH TIME ZONE,
    platform_user_id VARCHAR,
    platform_username VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## ⚙️ **Manual Database Setup**

### **Step 1: Create .env File**
```bash
# Copy the example file
cp env.example .env
```

### **Step 2: Configure Database Credentials**
Edit `.env` file:
```env
# Database Configuration
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/content_generator
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=content_generator

# Backend Configuration
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# OAuth Configuration
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret
TWITTER_CLIENT_ID=your-twitter-client-id
TWITTER_CLIENT_SECRET=your-twitter-client-secret
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
INSTAGRAM_APP_ID=your-instagram-app-id
INSTAGRAM_APP_SECRET=your-instagram-app-secret

# Email Configuration
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
```

### **Step 3: Start Database**
```bash
# Start only the database
docker-compose up -d postgres

# Or start all services
docker-compose up -d
```

### **Step 4: Create Tables**
The tables will be created automatically when the backend starts, or you can create them manually:

```bash
# Connect to PostgreSQL
docker exec -it content_generator_db psql -U your_username -d content_generator

# Or if using local PostgreSQL
psql -U your_username -d content_generator
```

### **Step 5: Verify Database**
```bash
# Check if tables exist
docker exec -it content_generator_db psql -U your_username -d content_generator -c "\dt"

# Check table structure
docker exec -it content_generator_db psql -U your_username -d content_generator -c "\d users"
```

## 🔧 **Database Management Commands**

### **Start/Stop Database**
```bash
# Start database only
docker-compose up -d postgres

# Stop database
docker-compose stop postgres

# Restart database
docker-compose restart postgres
```

### **Access Database**
```bash
# Connect to database
docker exec -it content_generator_db psql -U your_username -d content_generator

# List all tables
\dt

# Describe table structure
\d table_name

# Exit
\q
```

### **Reset Database**
```bash
# Stop all services
docker-compose down

# Remove database volume
docker volume rm marketing_postgres_data

# Start services again
docker-compose up -d
```

### **Backup Database**
```bash
# Create backup
docker exec content_generator_db pg_dump -U your_username content_generator > backup.sql

# Restore backup
docker exec -i content_generator_db psql -U your_username content_generator < backup.sql
```

## 🚀 **Quick Setup Commands**

```bash
# 1. Create .env file
cp env.example .env

# 2. Edit .env with your credentials
nano .env

# 3. Start database
docker-compose up -d postgres

# 4. Start backend (creates tables automatically)
docker-compose up -d backend

# 5. Start frontend
docker-compose up -d frontend

# 6. Check status
docker-compose ps
```

## 📊 **Database Connection Details**

- **Host:** localhost (or postgres container name)
- **Port:** 5432
- **Database:** content_generator
- **Username:** your_username (from .env)
- **Password:** your_password (from .env)
- **Connection String:** `postgresql://username:password@localhost:5432/content_generator`
