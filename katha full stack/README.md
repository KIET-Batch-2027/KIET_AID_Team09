# Katha AI - Tulu & Awadhi Story Generator

Full-stack Flask app for AI story generation in **English, Tulu, and Awadhi** with auth, profile, admin moderation, translation, TTS, and PDF download.

## Features

- User signup/login/logout with secure password hashing and session management
- Optional Firebase auth sync during signup (REST API)
- Story generation with Gemini API
- Languages: English, Tulu, Awadhi
- Genres: Folk, Kids, Moral, Horror, Devotional, Comedy, Fantasy, Adventure, Nature, Wisdom, Culture
- Lengths: Short (300), Medium (600), Long (1000)
- Child-safe mode
- Save stories per user
- Stories page + full story detail page
- Browser TTS (Voice `kn-IN`, `hi-IN`, `en-IN`) with play/pause/stop
- Voice input (speech-to-text) on prompt
- PDF download
- Admin dashboard (total users, stories, recent stories, delete story)
- Full website language switcher (English/Tulu/Awadhi)
- Profile page with avatar selection/upload, history delete, username/password update, delete account

## Folder Structure

```text
katha full stack/
+-- app/
¦   +-- __init__.py
¦   +-- decorators.py
¦   +-- extensions.py
¦   +-- firebase_service.py
¦   +-- i18n.py
¦   +-- models.py
¦   +-- utils.py
¦   +-- auth/
¦   +-- story/
¦   +-- admin/
¦   +-- templates/
¦   +-- static/
+-- config.py
+-- run.py
+-- requirements.txt
+-- schema.sql
+-- .env.example
+-- README.md
```

## Setup

1. Create virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Create environment file:

```bash
copy .env.example .env
```

3. Edit `.env` and set:

- `SECRET_KEY`
- `GEMINI_API_KEY`
- `FIREBASE_WEB_API_KEY` (optional)

4. Run app:

```bash
python run.py
```

5. Open:

- `http://127.0.0.1:5000`

## Admin Access

By default, all users are `user` role. Promote a user manually in SQLite:

```sql
UPDATE users SET role = 'admin' WHERE email = 'your-email@example.com';
```

## Story Function

Implemented in `app/story/services.py`:

- `generate_story(prompt, language, genre, length, child_safe=False, api_key='')`
- Adjusts word count by selected length
- Applies language-specific and genre-specific style
- Adds title format
- Ensures `Moral:` section for Moral genre
- Falls back safely if API is unavailable

## Notes

- Do not hardcode API keys in source files.
- Browser TTS voice availability depends on installed device/browser voices.
- Tulu TTS uses `kn-IN` voice mapping for best practical support.