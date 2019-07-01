from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

from .light_settings import *
from .task import *
from .message import *
from .account import *
from .light import *
from .gauge import *
from .user import *
