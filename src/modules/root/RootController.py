from flask import Blueprint, jsonify, render_template

root_blueprint = Blueprint('root', __name__)

@root_blueprint.route('', methods=['GET'])
def index():
    return render_template('home.html', segment='index')

@root_blueprint.route('usage', methods=['GET'])
def usage():
    return render_template('usage.html', segment='usage')

@root_blueprint.route('about', methods=['GET'])
def about():
    return render_template('about.html', segment='about')
