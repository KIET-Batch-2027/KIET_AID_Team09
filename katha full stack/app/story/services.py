import os
import re
from textwrap import dedent

import google.generativeai as genai

from app.i18n import LENGTHS

VOICE_MAP = {
    'tulu': 'kn-IN',
    'awadhi': 'hi-IN',
    'en': 'en-IN'
}

GENRE_GUIDE = {
    'Folk': 'Use oral-tradition style with cultural memory and community values.',
    'Kids': 'Keep language simple, playful, magical, and positive.',
    'Moral': 'Build toward a clear life lesson and add explicit moral at end.',
    'Horror': 'Use suspense and folklore darkness without graphic violence.',
    'Devotional': 'Use reverent tone, spiritual imagery, and faith-driven hope.',
    'Comedy': 'Include warm humor, funny misunderstandings, and light pacing.',
    'Fantasy': 'Add imaginative worldbuilding, magical rules, and wonder.',
    'Adventure': 'Add quest structure, challenges, and momentum.',
    'Nature': 'Center landscapes, seasons, animals, and ecological wisdom.',
    'Wisdom': 'Focus on reflection, proverbs, and elder guidance.',
    'Culture': 'Highlight festivals, customs, songs, and local identity.'
}


def get_word_count(length_key):
    for key, count in LENGTHS:
        if key == length_key:
            return count
    return 300


def _configure_model(api_key):
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')


def _fallback_story(prompt, language, genre, length_key):
    wc = get_word_count(length_key)
    lines = [
        f"Title: {genre} Story of {prompt.title()}",
        '',
        f"Once in a vibrant land, a tale began around \"{prompt}\". "
        f"This {genre.lower()} story is presented in {language.title()} style.",
        '',
        'The characters walked through conflict, courage, and discovery. '
        'Their choices shaped the ending and left a lasting emotion for the listener.',
        '',
        'The village remembered the story because it held truth, feeling, and shared memory.'
    ]
    if genre == 'Moral':
        lines.extend(['', 'Moral: Good choices, patience, and kindness shape destiny.'])
    return '\n'.join(lines) + f"\n\n(Approx target: {wc} words)"


def _remove_code_fences(text):
    return re.sub(r'^```[a-zA-Z]*|```$', '', text.strip(), flags=re.MULTILINE).strip()


def generate_story(prompt, language, genre, length, child_safe=False, api_key=''):
    word_count = get_word_count(length)

    tone_instruction = {
        'tulu': 'Write in Tulu with traditional coastal Karnataka storytelling rhythm and imagery.',
        'awadhi': 'Write in Awadhi with rural north Indian dialect flavor and oral storytelling cadence.',
        'en': 'Write in natural, expressive Indian English suitable for storytelling.'
    }.get(language, 'Write in English.')

    safe_instruction = (
        'Keep content child-safe and avoid explicit violence, abuse, hateful content, and sexual content.'
        if child_safe
        else 'Avoid harmful stereotypes and keep content respectful.'
    )

    genre_instruction = GENRE_GUIDE.get(genre, 'Keep a coherent narrative arc and emotional flow.')

    prompt_text = dedent(
        f"""
        Create a complete story with these rules:
        - Story prompt: {prompt}
        - Target language: {language}
        - Genre: {genre}
        - Target length: about {word_count} words
        - Language tone: {tone_instruction}
        - Genre style: {genre_instruction}
        - Safety: {safe_instruction}

        Formatting rules:
        1. Start with exactly one title line: Title: <title>
        2. Use clear paragraphs (short to medium paragraphs).
        3. Keep narrative coherent from beginning to ending.
        4. If genre is Moral, end with a final line: Moral: <clear moral lesson>
        5. Do not include markdown symbols.
        """
    ).strip()

    model = _configure_model(api_key or os.getenv('GEMINI_API_KEY', ''))
    if not model:
        return _fallback_story(prompt, language, genre, length)

    try:
        response = model.generate_content(prompt_text)
        story_text = _remove_code_fences(response.text or '')
        if not story_text:
            return _fallback_story(prompt, language, genre, length)

        if genre == 'Moral' and 'Moral:' not in story_text:
            story_text = story_text.rstrip() + '\n\nMoral: Kindness and wisdom create lasting good.'

        return story_text
    except Exception:
        return _fallback_story(prompt, language, genre, length)


def translate_story(story_text, target_language, api_key=''):
    if target_language == 'en':
        return story_text

    model = _configure_model(api_key or os.getenv('GEMINI_API_KEY', ''))
    if not model:
        return story_text

    instruction = (
        f"Translate this story into {target_language}. Keep title structure and meaning. "
        'Do not add commentary.'
    )

    try:
        response = model.generate_content(f"{instruction}\n\n{story_text}")
        return _remove_code_fences(response.text or story_text)
    except Exception:
        return story_text