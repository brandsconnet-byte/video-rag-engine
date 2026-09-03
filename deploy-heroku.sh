#!/bin/bash
# Deploy to Heroku

echo "🎬 Video RAG Engine - Heroku Deployment"
echo "========================================\n"

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found"
    echo "\nInstall from: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

echo "✅ Heroku CLI found\n"

# Login to Heroku
echo "Logging into Heroku..."
heroku login

# Create app name
read -p "Enter app name (must be unique): " APP_NAME

echo "\n📱 Creating Heroku app: $APP_NAME"
heroku create $APP_NAME

# Set buildpack for Python
echo "\n⚙️  Setting buildpack..."
heroku buildpacks:set heroku/python --app $APP_NAME

# Create Procfile if it doesn't exist
if [ ! -f "Procfile" ]; then
    echo "\n📝 Creating Procfile..."
    echo "web: python app.py" > Procfile
fi

# Deploy
echo "\n🚀 Deploying to Heroku..."
git push heroku main

echo "\n✅ Deployment complete!"
echo "\n🌐 Your app is live at: https://$APP_NAME.herokuapp.com"
echo "\n📊 View logs with: heroku logs --tail --app $APP_NAME"
