# AI Blog Generator (Django)

A Django web app that converts YouTube video transcripts into structured blog articles using OpenAI, then stores generated posts per user.

## Features

- User authentication (signup, login, logout)
- Generate blog posts from YouTube links
- Transcript extraction using `youtube-transcript-api`
- AI-powered blog generation using OpenAI Chat Completions
- Per-user blog history list and details page
- Media/static-ready Django configuration

## Tech Stack

- Python 3.10+
- Django 5.2
- MySQL
- OpenAI Python SDK
- YouTube Transcript API

## Project Structure

```text
.
|-- ai_blog_app/
|   |-- settings.py
|   |-- urls.py
|   `-- ...
|-- blog_generator/
|   |-- models.py
|   |-- views.py
|   |-- urls.py
|   `-- migrations/
|-- templates/
|   |-- index.html
|   |-- all-blogs.html
|   |-- blog-details.html
|   |-- login.html
|   `-- signup.html
|-- media/
|-- manage.py
|-- mydb.py
`-- requirements.txt
```

## How It Works

1. User logs in.
2. User submits a YouTube link.
3. App extracts the video ID and fetches transcript text.
4. Transcript is sent to OpenAI (`gpt-4.1-mini`) with a prompt to generate a polished blog in Markdown.
5. Generated blog is saved in MySQL and shown to the user.

## Prerequisites

- Python 3.10 or newer
- MySQL server running locally
- Git
- OpenAI API key

## Setup

### 1) Clone the repository

```bash
git clone <your-repo-url>
cd ai_blog_app
```

### 2) Create and activate virtual environment

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

> Note: if `requirements.txt` is UTF-16 encoded in your local copy and `pip` fails to parse it, re-save it as UTF-8 first.

```bash
pip install -r requirements.txt
```

### 4) Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 5) Configure MySQL

Current app settings expect:

- Database: `ai_blog_gen_db`
- Host: `localhost`
- Port: `3306`
- User/password from your Django settings

Option A: create DB using helper script:

```bash
python mydb.py
```

Option B: create manually in MySQL:

```sql
CREATE DATABASE ai_blog_gen_db;
```

### 6) Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7) Run development server

```bash
python manage.py runserver
```

Open: `http://127.0.0.1:8000/`

## App Routes

- `/` : Home page (requires login)
- `/login/` : Login page
- `/signup/` : Signup page
- `/logout/` : Logout
- `/generate-blog/` : POST endpoint for blog generation
- `/blog-list/` : User's generated blogs
- `/blog-details/<id>/` : Single blog details
- `/admin/` : Django admin

## Data Model

`BlogPost` fields:

- `user` (ForeignKey to Django User)
- `youtube_title`
- `youtube_link`
- `generated_content`
- `created_at`

## Development Notes

- `generate-blog` is CSRF-exempt in current implementation.
- The app currently uses MySQL credentials directly in `settings.py`.
- OpenAI model is configured in `blog_generator/views.py`.

## Recommended Security Improvements

Before deploying, update the following:

- Move DB credentials and Django secret key to environment variables
- Set `DEBUG = False`
- Set `ALLOWED_HOSTS` properly
- Re-enable CSRF protection for sensitive endpoints
- Use a production-ready web server and static/media strategy

## Troubleshooting

- Transcript not found / no captions:
  - Some videos do not provide captions, or captions are unavailable by region.
- OpenAI errors:
  - Ensure `.env` exists and `OPENAI_API_KEY` is valid.
- MySQL connection errors:
  - Verify server is running and credentials/database name match your settings.

## License

Add your preferred license in this section (for example, MIT).
