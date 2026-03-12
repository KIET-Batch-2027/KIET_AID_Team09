from flask import Blueprint

story_bp = Blueprint('story', __name__, url_prefix='/story')

from app.story import routes  # noqa: E402,F401