# Standard Library Imports
from flask import Flask
import os
from flask_cors import CORS

# Import blueprints
from .modules.root.RootController import root_blueprint
from .modules.chat.ChatController import chat_blueprint

# Import extensions
from .extensions import db, migrate


# Init App factory
def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configs
    app.config['UPLOAD_FOLDER'] = './static/uploads' 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.vwbiuwjzfxcvswivfina:GhNDbOBVrs03FMBw@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres'

    # Init DB
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    app.register_blueprint(root_blueprint, url_prefix='/')
    app.register_blueprint(chat_blueprint, url_prefix='/chat')

    
    return app

app = create_app()
