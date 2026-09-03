"""Lightning AI Studio App for Video RAG Engine."""

import lightning as L
from lightning.app.components import PythonServer
import subprocess
import sys


class VideoRAGServer(PythonServer):
    """Lightning AI server component for Video RAG Engine."""

    def __init__(self):
        super().__init__(
            port=5000,
            cloud_compute=L.CloudCompute("gpu"),  # Request GPU
        )

    def setup(self):
        """Install dependencies and setup models."""
        # Install requirements (torch already installed)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-lightning.txt"])
        
        # Download AI models
        from scripts.download_models import download_models
        download_models()
        
        # Start Flask app
        from app import app
        self.app = app

    def predict(self, request):
        """Handle predictions."""
        return {"status": "Video RAG Engine running on Lightning AI"}


class VideoRAGApp(L.LightningFlow):
    """Main Lightning App."""

    def __init__(self):
        super().__init__()
        self.server = VideoRAGServer()

    def run(self):
        self.server.run()

    def configure_layout(self):
        return {"name": "Video RAG Engine", "content": self.server.url}


app = L.LightningApp(VideoRAGApp())
