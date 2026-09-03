#!/usr/bin/env python3
"""One-command installation and deployment."""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(cmd, description):
    """Execute command with description."""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False)
        if result.returncode != 0:
            print(f"❌ {description} failed")
            return False
        print(f"✅ {description} complete")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def install_local():
    """Install and run locally."""
    print("\n" + "="*60)
    print("📦 LOCAL INSTALLATION")
    print("="*60)
    
    # Create virtual environment
    run_command("python3 -m venv venv", "Creating virtual environment")
    
    # Activate and install
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip")
    run_command(f"{pip_cmd} install -r requirements.txt flask", "Installing dependencies")
    run_command(f"{python_cmd} scripts/download_models.py", "Downloading AI models")
    
    print("\n" + "="*60)
    print("✅ LOCAL INSTALLATION COMPLETE")
    print("="*60)
    print("\n🚀 Start the app with:")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\python app.py")
    else:
        print("   source venv/bin/activate")
        print("   python app.py")
    print("\n🌐 Then visit: http://localhost:5000\n")


def install_docker():
    """Install using Docker."""
    print("\n" + "="*60)
    print("🐳 DOCKER INSTALLATION")
    print("="*60)
    
    if not run_command("docker --version", "Checking Docker"):
        print("\n❌ Docker not installed")
        print("Download from: https://www.docker.com/products/docker-desktop")
        return
    
    run_command("docker build -t video-rag-engine .", "Building Docker image")
    print("\n" + "="*60)
    print("✅ DOCKER INSTALLATION COMPLETE")
    print("="*60)
    print("\n🚀 Start with:")
    print("   docker run -p 5000:5000 video-rag-engine")
    print("\n🌐 Then visit: http://localhost:5000\n")


def instant_cloud_access():
    """Share localhost to internet with ngrok."""
    print("\n" + "="*60)
    print("☁️  INSTANT CLOUD ACCESS (via ngrok)")
    print("="*60)
    
    print("\n1️⃣  Sign up at: https://ngrok.com/signup")
    print("2️⃣  Copy your auth token")
    print("3️⃣  Run: ngrok config add-authtoken <YOUR_TOKEN>")
    print("4️⃣  Run: bash quick-share.sh")
    print("\n✅ Your app will be accessible from anywhere!\n")


def heroku_deploy():
    """Deploy to Heroku."""
    print("\n" + "="*60)
    print("☁️  HEROKU DEPLOYMENT")
    print("="*60)
    
    print("\n1️⃣  Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli")
    print("2️⃣  Run: bash deploy-heroku.sh")
    print("\n✅ App will be live at: https://your-app-name.herokuapp.com\n")


def aws_deploy():
    """Deploy to AWS."""
    print("\n" + "="*60)
    print("☁️  AWS DEPLOYMENT")
    print("="*60)
    
    print("\n1️⃣  Install AWS & EB CLI:")
    print("   pip install awsebcli")
    print("2️⃣  Configure AWS credentials:")
    print("   aws configure")
    print("3️⃣  Run: bash deploy-aws.sh")
    print("\n✅ App will be deployed to Elastic Beanstalk\n")


def main():
    """Main menu."""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║   🎬 VIDEO RAG ENGINE - DEPLOYMENT WIZARD                ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    print("\nChoose installation method:\n")
    print("1️⃣  📦 Local Installation (your computer)")
    print("2️⃣  🐳 Docker (containerized)")
    print("3️⃣  ☁️  Instant Cloud Access (ngrok - no deployment)")
    print("4️⃣  ⚡ Heroku Deployment (free tier available)")
    print("5️⃣  🚀 AWS Deployment (scalable)")
    print("6️⃣  📖 View all options\n")
    
    choice = input("Enter your choice (1-6): ").strip()
    
    if choice == "1":
        install_local()
    elif choice == "2":
        install_docker()
    elif choice == "3":
        instant_cloud_access()
    elif choice == "4":
        heroku_deploy()
    elif choice == "5":
        aws_deploy()
    elif choice == "6":
        print("\n📖 DEPLOYMENT OPTIONS\n")
        print("Local Installation:")
        print("  - Fast setup on your machine")
        print("  - Only accessible locally (http://localhost:5000)")
        print("  - No server costs")
        print("")
        print("Docker:")
        print("  - Containerized deployment")
        print("  - Easy to share and scale")
        print("  - Run on any machine with Docker")
        print("")
        print("Instant Cloud Access (ngrok):")
        print("  - Share localhost to internet instantly")
        print("  - No deployment or server setup needed")
        print("  - URL: https://xyz123.ngrok.io")
        print("")
        print("Heroku:")
        print("  - Free tier available")
        print("  - Automatic SSL/HTTPS")
        print("  - Easy rollback and scaling")
        print("  - URL: https://your-app.herokuapp.com")
        print("")
        print("AWS:")
        print("  - Most scalable option")
        print("  - Full control and customization")
        print("  - Pay only for what you use")
        print("  - URL: https://your-app.elasticbeanstalk.com")
        print("")
    else:
        print("❌ Invalid choice")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Installation cancelled")
        sys.exit(1)
