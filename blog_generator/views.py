from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import re
from .models import BlogPost

from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import os
from dotenv import load_dotenv


#  Initialize OpenAI client
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



# PAGE VIEWS


@login_required
def index(request):
    return render(request, 'index.html')



# BLOG GENERATION VIEW


@csrf_exempt
def generate_blog(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        yt_link = data.get('link')

        if not yt_link:
            return JsonResponse({'error': 'No YouTube link provided'}, status=400)

        # ✅ Extract video ID
        video_id = extract_video_id(yt_link)
        if not video_id:
            return JsonResponse({'error': 'Invalid YouTube URL'}, status=400)

        # ✅ Get transcript
        transcription = get_transcription(video_id)

        if transcription == "NO_CAPTIONS":
            return JsonResponse({'error': 'This video has no captions available. Try another video.'}, status=400)

        if not transcription:
            return JsonResponse({'error': 'Failed to fetch transcript'}, status=500)

        # ✅ Generate blog using OpenAI
        blog_content = generate_blog_from_transcription(transcription)

        if not blog_content:
            return JsonResponse({'error': 'Failed to generate blog article'}, status=500)

        
    
        # save blog post to database
        new_blog_article = BlogPost.objects.create(
            user = request.user,
            youtube_title=blog_content.split('\n')[0].replace('#', '').strip(),
            youtube_link = yt_link,
            generated_content = blog_content

        )
        new_blog_article.save()

        return JsonResponse({'content': blog_content})


    except Exception as e:
        print("Error in generate_blog:", e)
        return JsonResponse({'error': 'Something went wrong on the server'}, status=500)



#  HELPER FUNCTIONS


def extract_video_id(url):
    """
    Extract YouTube video ID from different URL formats
    """
    patterns = [
        r"(?:v=)([a-zA-Z0-9_-]+)",
        r"(?:youtu\.be/)([a-zA-Z0-9_-]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None




def get_transcription(video_id):
    try:
        ytt_api = YouTubeTranscriptApi()

        transcript = ytt_api.fetch(video_id)

        full_text = " ".join([entry.text for entry in transcript])
        return full_text

    except Exception as e:
        print("Transcript error:", e)
        return "NO_CAPTIONS"


def generate_blog_from_transcription(transcription):
    try:
        # ⚠️ Limit transcript size to avoid token overflow
        transcription = transcription[:12000]

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional blog writer."
                },
                {
                    "role": "user",
                    "content": f"""
Convert the following YouTube transcript into a well-structured blog article.

IMPORTANT:
- Use Markdown formatting
- Use # for title
- Use ## for section headings
- Use paragraphs properly
- Make it engaging and professional
- Remove filler words

Transcript:
{transcription}
"""
                }
            ],
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("OpenAI error:", e)
        return None


def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'all-blogs.html', {'blog_articles': blog_articles})


def blog_details(request, pk):
    blog_article_detail = BlogPost.objects.get(id=pk)
    if request.user == blog_article_detail.user:
        return render(request, 'blog-details.html', {'blog_article_detail': blog_article_detail})
    else:
        return redirect('/')

# AUTHENTICATION VIEWS


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {
                'error_message': "Invalid username or password"
            })

    return render(request, 'login.html')


def user_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repeatPassword = request.POST.get('repeatPassword')

        if password != repeatPassword:
            return render(request, 'signup.html', {
                'error_message': 'Passwords do not match'
            })

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            login(request, user)
            return redirect('/')
        except Exception as e:
            print("Signup error:", e)
            return render(request, 'signup.html', {
                'error_message': 'Error creating account'
            })

    return render(request, 'signup.html')


def user_logout(request):
    logout(request)
    return redirect('/')