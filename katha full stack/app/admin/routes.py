from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.admin import admin_bp
from app.decorators import admin_required
from app.extensions import db
from app.models import Story, User


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_stories = Story.query.count()
    recent_stories = Story.query.order_by(Story.created_at.desc()).limit(20).all()
    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_stories=total_stories,
        recent_stories=recent_stories
    )


@admin_bp.route('/delete-story/<int:story_id>', methods=['POST'])
@login_required
@admin_required
def delete_story(story_id):
    story = Story.query.get_or_404(story_id)
    db.session.delete(story)
    db.session.commit()
    flash('Story deleted by admin.', 'success')
    return redirect(url_for('admin.dashboard'))