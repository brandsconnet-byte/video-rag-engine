#!/bin/bash
# Deploy to AWS using Elastic Beanstalk

echo "🎬 Video RAG Engine - AWS Deployment"
echo "====================================\n"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found"
    echo "Install from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo "❌ Elastic Beanstalk CLI not found"
    echo "Install with: pip install awsebcli"
    exit 1
fi

echo "✅ AWS & EB CLI found\n"

# Initialize EB
echo "Initializing Elastic Beanstalk..."
eb init -p python-3.10 video-rag-engine --region us-east-1

# Create Procfile
if [ ! -f "Procfile" ]; then
    echo "📝 Creating Procfile..."
    echo "web: python app.py" > Procfile
fi

# Create environment
echo "\n🚀 Creating EB environment..."
eb create production

echo "\n✅ Deployment complete!"
echo "View your app with: eb open"
echo "View logs with: eb logs"
