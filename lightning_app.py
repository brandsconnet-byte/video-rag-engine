import lightning as L
from lightning.app.components import PythonServer
import os

class VideoRAGServer(PythonServer):
    def __init__(self):
        super().__init__(
            port=5000,
            cloud_compute=L.CloudCompute("gpu"),
        )

    def setup(self):
        # Install dependencies
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-lightning.txt"])
        
        # Import and setup Flask app
        from app import app
        self._app = app

    def predict(self, request):
        return {"status": "Video RAG Engine running"}

class VideoRAGApp(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.server = VideoRAGServer()

    def run(self):
        self.server.run()

    def configure_layout(self):
        return {"name": "Video RAG Engine", "content": self.server.url}

app = L.LightningApp(VideoRAGApp())
