import os

from flask import current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.auth import auth_bp
from app.extensions import db
from app.firebase_service import FirebaseAuthService
from app.models import Story, User
from app.utils import save_avatar_file

PRESET_AVATARS = [f'avatars/avatar{i}.svg' for i in range(1, 11)]


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.signup'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.signup'))

        if User.query.filter_by(email=email).first():
            flash('Email is already registered.', 'warning')
            return redirect(url_for('auth.signup'))

        firebase = FirebaseAuthService(current_app.config.get('FIREBASE_WEB_API_KEY', ''))
        ok, firebase_msg = firebase.signup(email, password)
        if not ok:
            flash(f'Firebase sync failed: {firebase_msg}', 'warning')

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='user'
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)
        session['site_lang'] = user.preferred_language
        flash('Signup successful. Welcome!', 'success')
        return redirect(url_for('home'))

    return render_template('auth/signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            session['site_lang'] = user.preferred_language
            flash('Login successful.', 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('home'))

        flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action', '')

        if action == 'change_username':
            new_username = request.form.get('new_username', '').strip()
            if new_username:
                current_user.username = new_username
                db.session.commit()
                flash('Username updated.', 'success')
            else:
                flash('Username cannot be empty.', 'warning')

        elif action == 'change_password':
            old_password = request.form.get('old_password', '')
            new_password = request.form.get('new_password', '')
            if not check_password_hash(current_user.password_hash, old_password):
                flash('Current password is incorrect.', 'danger')
            elif len(new_password) < 6:
                flash('New password must be at least 6 characters.', 'warning')
            else:
                current_user.password_hash = generate_password_hash(new_password)
                db.session.commit()
                flash('Password updated.', 'success')

        elif action == 'select_avatar':
            avatar = request.form.get('avatar', '')
            if avatar in PRESET_AVATARS:
                current_user.avatar = avatar
                db.session.commit()
                flash('Avatar updated.', 'success')

        elif action == 'upload_avatar':
            avatar_file = request.files.get('avatar_file')
            saved_path = save_avatar_file(avatar_file)
            if saved_path:
                current_user.avatar = saved_path
                db.session.commit()
                flash('Avatar uploaded.', 'success')
            else:
                flash('Invalid avatar file type.', 'warning')

        elif action == 'delete_story':
            story_id = request.form.get('story_id', type=int)
            story = Story.query.filter_by(id=story_id, user_id=current_user.id).first()
            if story:
                db.session.delete(story)
                db.session.commit()
                flash('Story deleted from your history.', 'success')

        elif action == 'delete_account':
            uid = current_user.id
            logout_user()
            user = User.query.get(uid)
            if user:
                db.session.delete(user)
                db.session.commit()
            flash('Account deleted permanently.', 'success')
            return redirect(url_for('home'))

        return redirect(url_for('auth.profile'))

    stories = Story.query.filter_by(user_id=current_user.id).order_by(Story.created_at.desc()).all()
    return render_template('profile/profile.html', stories=stories, preset_avatars=PRESET_AVATARS)