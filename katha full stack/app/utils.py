import os
import re
from uuid import uuid4

from flask import current_app, session
from werkzeug.utils import secure_filename

from app.i18n import tr


def get_site_language():
    lang = session.get('site_lang', 'en')
    return lang if lang in {'en', 'tulu', 'awadhi'} else 'en'


def t(key):
    return tr(get_site_language(), key)


def allowed_file(filename):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_IMAGE_EXTENSIONS']


def save_avatar_file(file_storage):
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        return None

    filename = secure_filename(file_storage.filename)
    unique_name = f"{uuid4().hex}_{filename}"
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_name)
    file_storage.save(file_path)
    return f"uploads/{unique_name}"


def clean_for_tts(text):
    # Remove punctuation that sounds unnatural in speech synthesis.
    return re.sub(r"[\*\"'`:;!?#~.,()\[\]{}]", ' ', text)