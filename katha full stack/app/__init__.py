from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import current_user

from config import Config
from app.extensions import db, login_manager
from app.i18n import LANGUAGE_OPTIONS
from app.models import Story, User
from app.utils import get_site_language, t


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from app.auth.routes import auth_bp
    from app.story.routes import story_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(story_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_globals():
        return {
            't': t,
            'site_lang': get_site_language(),
            'language_options': LANGUAGE_OPTIONS
        }

    @app.before_request
    def sync_language_from_user():
        if 'site_lang' not in session:
            session['site_lang'] = 'en'
        if current_user.is_authenticated and current_user.preferred_language in {'en', 'tulu', 'awadhi'}:
            if request.endpoint != 'set_language' and request.method == 'GET':
                session['site_lang'] = current_user.preferred_language

    @app.route('/')
    def home():
        total_users = User.query.count()
        total_stories = Story.query.count()
        recent_stories = Story.query.order_by(Story.created_at.desc()).limit(6).all()
        return render_template(
            'home.html',
            total_users=total_users,
            total_stories=total_stories,
            recent_stories=recent_stories
        )

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/set-language', methods=['POST'])
    def set_language():
        lang = request.form.get('site_lang', 'en')
        if lang not in {'en', 'tulu', 'awadhi'}:
            lang = 'en'
        session['site_lang'] = lang
        if current_user.is_authenticated:
            current_user.preferred_language = lang
            db.session.commit()
        next_url = request.form.get('next') or request.referrer or url_for('home')
        return redirect(next_url)

    @app.errorhandler(403)
    def forbidden(_error):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    @app.errorhandler(404)
    def not_found(_error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(_error):
        db.session.rollback()
        flash('An unexpected error occurred.', 'danger')
        return redirect(url_for('home'))

    with app.app_context():
        db.create_all()

    return app