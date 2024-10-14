## Import the required libraries
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
import os

## Import the app
from .ChatService import ChatService

## Initialize the chat blueprint
chat_blueprint = Blueprint('chat', __name__)

## Initialize the chat service
chat_service = ChatService()

@chat_blueprint.route('', methods=['GET'])
def chat():
    return render_template('chat.html', segment='chat')

@chat_blueprint.route('/analyze', methods=['GET'])
def analyze():
    result = chat_service.read_image()
    return jsonify({'message':result})

@chat_blueprint.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file:
        # Save the uploaded file to /static/uploads
        filepath = os.path.join('src/static/upload/', file.filename)
        file.save(filepath)
        return redirect(url_for('chat.chat'))    

