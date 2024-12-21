from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS)
socketio = SocketIO(app)

app.config.from_object('app.config.Config')  # Load config from Config class

from app import routes  # Import routes at the end to avoid circular imports
