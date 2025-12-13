# Quick Start: Deploy to Render in 5 Minutes

## Fast Track Deployment

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Ready for Render deployment"
   git push origin main
   ```

2. **Create PostgreSQL Database on Render**
   - Go to Render Dashboard → New + → PostgreSQL
   - Name: `terrabia-db`
   - Plan: Free
   - Click "Create Database"
   - Copy the "Internal Database URL"

3. **Create Web Service on Render**
   - Go to Render Dashboard → New + → Web Service
   - Connect your GitHub repository
   - Configure:
     - **Name**: `terrabia-web`
     - **Build Command**: `./build.sh`
     - **Start Command**: `gunicorn myapp.wsgi:application`
     - **Plan**: Free

4. **Set Environment Variables**
   In your web service → Environment → Add:
   
   ```
   SECRET_KEY = [Generate using: python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"]
   DEBUG = False
   ALLOWED_HOSTS = *.onrender.com
   DATABASE_URL = [Paste the Internal Database URL from step 2]
   ```

5. **Link Database**
   - In web service → Environment → Link Database
   - Select your PostgreSQL database
   - This auto-sets DATABASE_URL

6. **Deploy!**
   - Click "Save Changes"
   - Render will build and deploy automatically
   - Wait for "Live" status

7. **Create Superuser** (after first deploy)
   - Go to your service → Shell tab
   - Run: `python manage.py createsuperuser`

## That's it! Your app is live! 🎉

For detailed instructions, see `DEPLOYMENT.md`
