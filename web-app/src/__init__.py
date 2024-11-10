# Standard Library Imports
from flask import Flask
from flask_cors import CORS

# Import blueprints
from .modules.root.RootController import root_blueprint
from .modules.chat.ChatController import chat_blueprint


# Init App factory
def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configs
    app.config['UPLOAD_FOLDER'] = './static/uploads' 
    app.config['SECRET_KEY'] = 'my_secret'

    # Register blueprints
    app.register_blueprint(root_blueprint, url_prefix='/')
    app.register_blueprint(chat_blueprint, url_prefix='/chat')

    
    return app

app = create_app()
