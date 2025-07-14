# PostrAI Backend Deployment Guide

This guide will help you deploy the PostrAI backend to Render.

## Prerequisites

1. A [Render](https://render.com) account
2. A GitHub repository with your code
3. A MongoDB Atlas database (or any MongoDB instance accessible from the internet)

## ⚠️ Important: MongoDB SSL Configuration

If you encounter SSL handshake errors during deployment, your MongoDB connection has been updated to handle SSL/TLS issues common in cloud environments. The connection configuration now includes:

- SSL context configuration
- Certificate validation bypass for cloud compatibility
- Extended timeout settings
- Connection pooling optimization

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
4. **Important**: Update your IP whitelist to allow connections from `0.0.0.0/0` (all IPs) for Render deployment
5. Get your connection string in this format:
   ```
   mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority&ssl=true&tlsAllowInvalidCertificates=true
   ```

### 3. MongoDB Connection String Format

For Render deployment, use this connection string format:

```
mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority&ssl=true&tlsAllowInvalidCertificates=true&connectTimeoutMS=30000&socketTimeoutMS=30000&serverSelectionTimeoutMS=30000
```

Replace:
- `username`: Your MongoDB username
- `password`: Your MongoDB password
- `cluster`: Your cluster name
- `database`: Your database name

### 4. Deploy to Render

#### Option A: Using render.yaml (Recommended)

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Blueprint"
4. Connect your GitHub repository
5. Render will automatically detect the `render.yaml` file
6. Set the required environment variable:
   - `MONGODB_URI`: Your MongoDB connection string (with SSL parameters)

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
   - `MONGODB_URI`: Your MongoDB connection string (with SSL parameters)
   - `PORT`: `8000` (automatically set by Render)

6. Click "Create Web Service"

### 5. Configure Environment Variables

In your Render service settings, add:

```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority&ssl=true&tlsAllowInvalidCertificates=true&connectTimeoutMS=30000&socketTimeoutMS=30000&serverSelectionTimeoutMS=30000
PORT=8000
PYTHONUNBUFFERED=1
```

### 6. MongoDB Atlas Network Access

**Critical**: In MongoDB Atlas, make sure to:
1. Go to "Network Access" in your Atlas dashboard
2. Add IP Address: `0.0.0.0/0` (Allow access from anywhere)
3. This is required for Render to connect to your database

### 7. Update CORS Settings (if needed)

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

5. **SSL/TLS**: The MongoDB connection is configured to handle SSL issues in cloud environments

## Troubleshooting

### Common Issues

1. **SSL Handshake Errors**: 
   - Ensure your MongoDB connection string includes SSL parameters
   - Check that MongoDB Atlas allows connections from `0.0.0.0/0`
   - The code has been updated to handle SSL/TLS issues

2. **Build Failures**: Check the build logs in Render dashboard

3. **Connection Timeouts**: 
   - Verify your MongoDB connection string
   - Check MongoDB Atlas network access settings

4. **CORS Errors**: Update the allowed origins in your FastAPI app

5. **Port Issues**: Render automatically sets the PORT environment variable

### Debugging Steps

1. Check the service logs in Render dashboard
2. Verify MongoDB Atlas network access is set to `0.0.0.0/0`
3. Test your MongoDB connection string locally
4. Ensure environment variables are set correctly in Render

### MongoDB Atlas Checklist

- [ ] Database user created with proper permissions
- [ ] Network access set to `0.0.0.0/0` (allow from anywhere)
- [ ] Connection string includes SSL parameters
- [ ] Database name is correct in the connection string

## Scaling

For production use, consider:
- Upgrading to a paid Render plan
- Using a dedicated MongoDB cluster
- Implementing proper logging and monitoring
- Adding rate limiting and security measures
- Restricting MongoDB network access to specific IPs in production

## Support

- [Render Documentation](https://render.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [PyMongo SSL Documentation](https://pymongo.readthedocs.io/en/stable/examples/tls.html) 