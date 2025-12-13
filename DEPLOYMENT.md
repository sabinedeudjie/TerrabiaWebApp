# Deployment Guide for Terrabia Web on Render

This guide will walk you through deploying your Django application to Render.

## Prerequisites

1. A GitHub account
2. A Render account (sign up at https://render.com)
3. Your code pushed to a GitHub repository

## Step-by-Step Deployment Process

### 1. Prepare Your Repository

Make sure all your files are committed and pushed to GitHub:

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create a PostgreSQL Database on Render

1. Log in to your Render dashboard
2. Click "New +" and select "PostgreSQL"
3. Configure the database:
   - **Name**: `terrabia-db` (or any name you prefer)
   - **Database**: `terrabia_db`
   - **User**: `terrabia_user`
   - **Region**: Choose the closest region to your users
   - **Plan**: Start with Free tier (upgrade later if needed)
4. Click "Create Database"
5. **Important**: Copy the "Internal Database URL" - you'll need this later

### 3. Create a Web Service on Render

1. In your Render dashboard, click "New +" and select "Web Service"
2. Connect your GitHub repository:
   - Click "Connect GitHub"
   - Authorize Render to access your repositories
   - Select the repository containing your Terrabia Web project
3. Configure the service:
   - **Name**: `terrabia-web` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn myapp.wsgi:application`
   - **Plan**: Start with Free tier

### 4. Configure Environment Variables

In your Render web service settings, go to "Environment" and add these variables:

#### Required Variables:

- **SECRET_KEY**: Generate a secure secret key:
  ```python
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
  Or use: `python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

- **DEBUG**: Set to `False` for production

- **ALLOWED_HOSTS**: Set to your Render URL (e.g., `terrabia-web.onrender.com`) or use `*.onrender.com` to allow all Render subdomains

- **DATABASE_URL**: 
  - Go to your PostgreSQL database dashboard
  - Copy the "Internal Database URL"
  - Paste it as the `DATABASE_URL` environment variable

#### Optional Variables:

- **PYTHON_VERSION**: `3.11.0` (or your preferred Python version)

### 5. Link Database to Web Service

1. In your web service dashboard, go to "Environment"
2. Click "Link Database" or manually add the database connection
3. Render will automatically set the `DATABASE_URL` environment variable

### 6. Deploy

1. Click "Save Changes" in your web service settings
2. Render will automatically start building and deploying your application
3. Monitor the build logs to ensure everything deploys successfully

### 7. Run Initial Setup Commands (if needed)

After the first deployment, you may need to:

1. Create a superuser:
   - Go to your service's "Shell" tab in Render
   - Run: `python manage.py createsuperuser`

2. Load initial data (if you have fixtures or management commands):
   - Run: `python manage.py create_yaounde_locations` (if needed)
   - Run: `python manage.py create_categories` (if needed)

### 8. Configure Static Files

Static files are automatically handled by WhiteNoise. The build script runs `collectstatic` automatically.

### 9. Media Files Storage

**Important**: Render's free tier has ephemeral storage, meaning uploaded files will be lost on redeploy. For production, consider:

- Using AWS S3 or similar cloud storage
- Using Render's persistent disk (paid plans)
- Using a dedicated file storage service

To configure S3 (recommended for production):
1. Install `django-storages` and `boto3`
2. Add to `requirements.txt`:
   ```
   django-storages>=1.14.0
   boto3>=1.28.0
   ```
3. Update `settings.py` to use S3 for media files

## Alternative: Using render.yaml (Blueprints)

If you prefer to use Render Blueprints:

1. The `render.yaml` file is already configured
2. In Render dashboard, click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect and use `render.yaml`
5. Review and apply the configuration

## Post-Deployment Checklist

- [ ] Verify the site is accessible
- [ ] Test user registration and login
- [ ] Test all major features
- [ ] Create a superuser account
- [ ] Set up email service (if needed)
- [ ] Configure custom domain (optional)
- [ ] Set up SSL certificate (automatic on Render)
- [ ] Configure backup strategy for database

## Troubleshooting

### Build Fails

- Check build logs for specific errors
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility

### Database Connection Issues

- Verify `DATABASE_URL` is set correctly
- Check database is running and accessible
- Ensure database is linked to web service

### Static Files Not Loading

- Verify `collectstatic` runs in build script
- Check `STATIC_ROOT` and `STATIC_URL` settings
- Ensure WhiteNoise middleware is in `MIDDLEWARE`

### 500 Errors

- Check application logs in Render dashboard
- Verify `DEBUG=False` and check error pages
- Review environment variables

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | (auto-generated) |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed hostnames | `terrabia-web.onrender.com` |
| `DATABASE_URL` | PostgreSQL connection string | (auto-set by Render) |
| `PYTHON_VERSION` | Python version | `3.11.0` |

## Security Notes

- Never commit `SECRET_KEY` or sensitive data to Git
- Always use `DEBUG=False` in production
- Keep `ALLOWED_HOSTS` restricted to your domain
- Regularly update dependencies
- Use strong passwords for database and admin accounts

## Updating Your Application

1. Make changes locally
2. Test thoroughly
3. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your update message"
   git push origin main
   ```
4. Render will automatically detect changes and redeploy

## Support

For issues specific to:
- **Render**: Check Render documentation at https://render.com/docs
- **Django**: Check Django deployment documentation
- **This project**: Review the codebase and error logs
