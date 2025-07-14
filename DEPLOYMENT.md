# PostrAI Backend Deployment Guide

This guide will help you deploy the PostrAI backend to Render.

## Prerequisites

1. A [Render](https://render.com) account
2. A GitHub repository with your code
3. A MongoDB Atlas database (or any MongoDB instance accessible from the internet)

## Deployment Steps

### 1. Prepare Your Repository

Make sure your repository contains:
- `Dockerfile`
- `requirements.txt`
- `render.yaml` (optional, for easier deployment)
- `.dockerignore`
- All your application files

### 2. Set Up MongoDB Atlas (if not already done)

1. Go to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Create a new cluster or use an existing one
3. Create a database user with read/write permissions
4. Get your connection string (it should look like: `mongodb+srv://username:password@cluster.mongodb.net/database`)

### 3. Deploy to Render

#### Option A: Using render.yaml (Recommended)

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Blueprint"
4. Connect your GitHub repository
5. Render will automatically detect the `render.yaml` file
6. Set the required environment variable:
   - `MONGODB_URI`: Your MongoDB connection string

#### Option B: Manual Setup

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `postrai-backend`
   - **Environment**: `Docker`
   - **Plan**: `Free` (or higher)
   - **Region**: Choose your preferred region
   - **Branch**: `main` (or your default branch)
   - **Dockerfile Path**: `./Dockerfile`

5. Set environment variables:
   - `MONGODB_URI`: Your MongoDB connection string
   - `PORT`: `8000` (automatically set by Render)

6. Click "Create Web Service"

### 4. Configure Environment Variables

In your Render service settings, add:

```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
PORT=8000
PYTHONUNBUFFERED=1
```

### 5. Update MongoDB Connection String

Make sure your MongoDB connection string in `database/mongodb.py` uses the environment variable:

```python
self.uri = os.getenv("MONGODB_URI", "your-fallback-connection-string")
```

### 6. Update CORS Settings (if needed)

If you're deploying a frontend, update the CORS origins in `app_main.py` to include your frontend URL:

```python
allow_origins=[
    "http://localhost:8080", 
    "http://127.0.0.1:8080",
    "http://localhost:3000",
    "https://your-frontend-domain.com",
    "https://*.onrender.com",
    "https://*.vercel.app",
    "https://*.netlify.app"
],
```

## Post-Deployment

### 1. Test Your API

Once deployed, your API will be available at:
- `https://your-service-name.onrender.com`

Test the health endpoint:
```bash
curl https://your-service-name.onrender.com/api/health
```

### 2. API Documentation

Access the interactive API documentation at:
- `https://your-service-name.onrender.com/docs`

### 3. Monitor Your Service

- Check the Render dashboard for logs and metrics
- Monitor the health check endpoint
- Set up alerts if needed

## Important Notes

1. **Free Tier Limitations**: Render's free tier has limitations:
   - Services spin down after 15 minutes of inactivity
   - 750 hours per month limit
   - Slower cold starts

2. **Environment Variables**: Never commit sensitive data like MongoDB connection strings to your repository

3. **CORS**: Make sure to update CORS settings when you deploy your frontend

4. **Health Checks**: The health check endpoint (`/api/health`) is configured to monitor your service

## Troubleshooting

### Common Issues

1. **Build Failures**: Check the build logs in Render dashboard
2. **Connection Issues**: Verify your MongoDB connection string
3. **CORS Errors**: Update the allowed origins in your FastAPI app
4. **Port Issues**: Render automatically sets the PORT environment variable

### Debugging

- Check the service logs in Render dashboard
- Test endpoints locally before deploying
- Verify environment variables are set correctly

## Scaling

For production use, consider:
- Upgrading to a paid Render plan
- Using a dedicated MongoDB cluster
- Implementing proper logging and monitoring
- Adding rate limiting and security measures

## Support

- [Render Documentation](https://render.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/) 