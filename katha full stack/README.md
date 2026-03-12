📖 Katha AI – Tulu & Awadhi Story Generator

Katha AI is a full-stack Flask web application that generates AI-powered stories in English, Tulu, and Awadhi.
It includes user authentication, profile management, admin moderation, translation, text-to-speech (TTS), and PDF download features.

✨ Features
🔐 Authentication

User Signup / Login / Logout

Secure password hashing

Session management

Optional Firebase authentication sync during signup (REST API)

🤖 AI Story Generation

Story generation using Gemini API

Supports multiple languages, genres, and story lengths

🌍 Supported Languages

English

Tulu

Awadhi

🎭 Story Genres

Folk

Kids

Moral

Horror

Devotional

Comedy

Fantasy

Adventure

Nature

Wisdom

Culture

📏 Story Length Options

Short – 300 words

Medium – 600 words

Long – 1000 words

🛡 Child Safe Mode

Generates family-friendly and safe stories for kids.

📚 Story Management

Save stories per user

Dedicated Stories page

Full story detail page

🔊 Voice Features

Browser Text-to-Speech (TTS)

Voices supported:

kn-IN

hi-IN

en-IN

Controls: Play / Pause / Stop

🎤 Voice Input

Speech-to-Text prompt input for story generation.

📄 Export

Download generated stories as PDF files

👨‍💻 Admin Dashboard

Admin panel includes:

Total users

Total stories

Recent stories

Option to delete stories

🌐 Language Switcher

Switch the entire website language between:

English

Tulu

Awadhi

👤 User Profile

Profile page features:

Avatar selection or upload

Delete story history

Update username

Change password

Delete account
katha full stack/
│
├── app/
│   ├── __init__.py
│   ├── decorators.py
│   ├── extensions.py
│   ├── firebase_service.py
│   ├── i18n.py
│   ├── models.py
│   ├── utils.py
│   │
│   ├── auth/
│   ├── story/
│   ├── admin/
│   ├── templates/
│   └── static/
│
├── config.py
├── run.py
├── requirements.txt
├── schema.sql
├── .env.example
└── README.md
⚙️ Setup
1️⃣ Create Virtual Environment
python -m venv .venv
2️⃣ Activate Virtual Environment
.venv\Scripts\activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Create Environment File
copy .env.example .env

Edit .env and add:

SECRET_KEY
GEMINI_API_KEY
FIREBASE_WEB_API_KEY (optional)
5️⃣ Run the Application
python run.py

Open the application in your browser:

http://127.0.0.1:5000
👑 Admin Access

By default, every user has the user role.

To promote a user to admin, run the following query in SQLite:

UPDATE users 
SET role = 'admin' 
WHERE email = 'your-email@example.com';
🧠 Story Generation Function

Implemented in:

app/story/services.py

Function:
generate_story(prompt, language, genre, length, child_safe=False, api_key='')

Function behavior:

Adjusts word count based on selected length

Applies language-specific style

Applies genre-specific storytelling

Automatically adds story title

Ensures "Moral:" section for Moral genre

Provides safe fallback if API is unavailable

⚠️ Notes

Do not hardcode API keys in source files.

Browser TTS voice availability depends on device/browser voices.

Tulu TTS uses kn-IN voice mapping.


