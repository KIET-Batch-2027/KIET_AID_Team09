import io
from datetime import datetime

from flask import Response, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

from app.extensions import db
from app.i18n import GENRES, LANGUAGE_OPTIONS, LENGTHS
from app.models import Story
from app.story import story_bp
from app.story.services import VOICE_MAP, generate_story, translate_story
from app.utils import clean_for_tts


@story_bp.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    generated_story = None
    saved_story = None
    selected = {
        'prompt': '',
        'language': 'en',
        'genre': 'Folk',
        'length': 'short',
        'child_safe': False
    }

    if request.method == 'POST':
        selected['prompt'] = request.form.get('prompt', '').strip()
        selected['language'] = request.form.get('language', 'en')
        selected['genre'] = request.form.get('genre', 'Folk')
        selected['length'] = request.form.get('length', 'short')
        selected['child_safe'] = bool(request.form.get('child_safe'))

        if not selected['prompt']:
            flash('Please enter a story prompt.', 'warning')
            return redirect(url_for('story.generate'))

        generated_story = generate_story(
            prompt=selected['prompt'],
            language=selected['language'],
            genre=selected['genre'],
            length=selected['length'],
            child_safe=selected['child_safe'],
            api_key=current_app.config.get('GEMINI_API_KEY', '')
        )

        story = Story(
            user_id=current_user.id,
            prompt=selected['prompt'],
            language=selected['language'],
            genre=selected['genre'],
            length=selected['length'],
            story_text=generated_story,
            is_child_safe=selected['child_safe']
        )
        db.session.add(story)
        db.session.commit()
        saved_story = story
        flash('Story generated and saved.', 'success')

    return render_template(
        'story/generate.html',
        generated_story=generated_story,
        saved_story=saved_story,
        genres=GENRES,
        lengths=LENGTHS,
        languages=LANGUAGE_OPTIONS,
        selected=selected,
        voice_map=VOICE_MAP
    )


@story_bp.route('/stories')
@login_required
def my_stories():
    stories = Story.query.filter_by(user_id=current_user.id).order_by(Story.created_at.desc()).all()
    return render_template('story/my_stories.html', stories=stories)


@story_bp.route('/stories/<int:story_id>')
@login_required
def view_story(story_id):
    story = Story.query.filter_by(id=story_id, user_id=current_user.id).first_or_404()
    return render_template('story/story_detail.html', story=story, voice_map=VOICE_MAP)


@story_bp.route('/stories/<int:story_id>/pdf')
@login_required
def download_pdf(story_id):
    story = Story.query.filter_by(id=story_id, user_id=current_user.id).first_or_404()

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawString(50, y, f"Katha AI Story - {story.genre} ({story.language})")

    y -= 24
    pdf.setFont('Helvetica', 10)
    pdf.drawString(50, y, f"Generated: {story.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

    y -= 24
    pdf.setFont('Helvetica', 11)

    for para in story.story_text.split('\n'):
        lines = simpleSplit(para, 'Helvetica', 11, width - 100)
        if not lines:
            y -= 14
            continue
        for line in lines:
            if y < 70:
                pdf.showPage()
                pdf.setFont('Helvetica', 11)
                y = height - 50
            pdf.drawString(50, y, line)
            y -= 14

    pdf.save()
    buffer.seek(0)
    filename = f"katha_story_{story.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
    return Response(
        buffer,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment;filename={filename}'}
    )


@story_bp.route('/translate', methods=['POST'])
@login_required
def translate():
    data = request.get_json(silent=True) or {}
    text = data.get('text', '').strip()
    target_language = data.get('language', 'en')

    if not text:
        return jsonify({'ok': False, 'error': 'Missing text'}), 400

    translated = translate_story(
        story_text=text,
        target_language=target_language,
        api_key=current_app.config.get('GEMINI_API_KEY', '')
    )
    return jsonify(
        {
            'ok': True,
            'text': translated,
            'clean_tts': clean_for_tts(translated),
            'voice': VOICE_MAP.get(target_language, 'en-IN')
        }
    )
