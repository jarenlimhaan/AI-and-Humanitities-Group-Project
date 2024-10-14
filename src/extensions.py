## This is just to follow the app factory pattern: https://flask.palletsprojects.com/en/1.1.x/patterns/appfactories/
## If not will have circular import issues regarding the db object

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()