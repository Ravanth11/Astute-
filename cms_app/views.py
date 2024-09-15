from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404, HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from rest_framework import viewsets
from .models import BlogPost
from .serializers import BlogPostSerializer
import markdown2
from .models import BlogPost, Images
import uuid
import io

def home(request):
    return render(request, "home.html", {'user': request.user})

@login_required
def blog_post(request):
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        thumbnail = request.POST['thumbnail']
        md_content = request.POST['content']
        date_created = timezone.now()
        html_content = markdown2.markdown(md_content)

        blog_post = BlogPost(title=title,
                             content_md=md_content,
                             content_html=html_content,
                             thumbnail=thumbnail,
                             author=author,
                             date_created=date_created)
        blog_post.save()
        messages.success(request, "Blog Post Created!")
        return redirect('home')

    return render(request, "create.html", {'user': request.user})

def get_blog(request, id):
    blog_post = get_object_or_404(BlogPost, id=id)
    response = {
        'id': blog_post.id,
        'title': blog_post.title,
        'author': blog_post.author,
        'thumbnail': blog_post.thumbnail,
        'content': blog_post.content_html,
        'date_created': blog_post.date_created
    }
    return JsonResponse(response, status=200)

@login_required
def manage(request):
    posts = BlogPost.objects.order_by('-id').all()
    return render(request, "manage.html", {'user': request.user, 'posts': posts})

@login_required
def view_post(request, id):
    blog_post = get_object_or_404(BlogPost, id=id)
    response = {
        'id': blog_post.id,
        'title': blog_post.title,
        'author': blog_post.author,
        'thumbnail': blog_post.thumbnail,
        'content': blog_post.content_html,
        'date_created': blog_post.date_created
    }
    return render(request, "blog.html", {'user': request.user, 'res': response})

@login_required
def delete(request, id):
    post = get_object_or_404(BlogPost, id=id)
    post.delete() 
    messages.success(request, "Blog Post Deleted!")
    return redirect('manage')

@login_required
def update_blog(request, id):
    blog_post = get_object_or_404(BlogPost, id=id)
    if request.method == 'POST':
        blog_post.title = request.POST['title']
        blog_post.author = request.POST['author']
        blog_post.thumbnail = request.POST['thumbnail']
        blog_post.content_md = request.POST['content']
        blog_post.content_html = markdown2.markdown(blog_post.content_md)
        blog_post.date_created = timezone.now()
        blog_post.save()
        messages.success(request, "Blog Post Updated!")
        return redirect('manage')

    return render(request, "update.html", {'blog_post': blog_post, 'user': request.user})

def upload_image(request):
    if 'image' not in request.FILES:
        return JsonResponse({'error': 'No file part'}, status=400)

    file = request.FILES['image']
    if not file:
        return JsonResponse({'error': 'No selected file'}, status=400)

    filename = file.name
    image_data = file.read()
    image_uuid = str(uuid.uuid4())
    image_url = request.build_absolute_uri(reverse('get_image', args=[image_uuid]))

    new_image = Images(image_name=filename, image_data=image_data, url=image_url)
    new_image.save()
    return JsonResponse({'url': image_url}, status=201)

def get_image(request, image_uuid):
    image = get_object_or_404(Images, url=request.build_absolute_uri(reverse('get_image', args=[image_uuid])))
    return HttpResponse(io.BytesIO(image.image_data), content_type='image/jpeg')
@login_required
def asset_manager(request):
    images = Images.objects.order_by('-id').all()
    print(images)
    return render(request, 'assets.html', {'images': images, 'user': request.user})



def delete_image(request, id):
    image = get_object_or_404(Images, id=id)
    image.delete()
    messages.success(request, "Image deleted!")
    return redirect('asset_manager')



def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                login(request, user)
                messages.success(request, 'Logged in!')
                return redirect('home')
            else:
                messages.error(request, 'Incorrect credentials.')
        except User.DoesNotExist:
            messages.error(request, 'User does not exist.')
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def sign_up_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password')
        password2 = request.POST.get('confirm-password')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        elif not email.endswith('@astute.ai'):
            messages.error(request, 'Permission Denied.')
        elif len(email) < 4:
            messages.error(request, 'Email must be greater than 3 characters.')
        elif len(username) < 2:
            messages.error(request, 'Username must be greater than 1 character.')
        elif password1 != password2:
            messages.error(request, 'Passwords don’t match.')
        elif len(password1) < 7:
            messages.error(request, 'Password must be at least 7 characters.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            messages.success(request, 'Account Created!')
            login(request, user)
            return redirect('home')
    return render(request, 'sign_up.html')
def blog_list(request):
    posts = BlogPost.objects.all()
    return render(request, 'blog_list.html', {'posts': posts})

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer

from django.http import JsonResponse
from .models import BlogPost

def fetch_all_posts(request):
    posts = BlogPost.objects.order_by('-id').all()
    response = []
    for post in posts:
        response.append({
            'id': post.id,
            'title': post.title,
            'author': post.author,
            'thumbnail': post.thumbnail,
            'content': post.content_html,
            'date_created': post.date_created
        })
    return JsonResponse(response, safe=False)

def fetch_6_posts(request):
    posts = BlogPost.objects.order_by('-id')[:6]
    response = []
    for post in posts:
        response.append({
            'id': post.id,
            'title': post.title,
            'author': post.author,
            'thumbnail': post.thumbnail,
            'content': post.content_html,
            'date_created': post.date_created
        })
    return JsonResponse(response, safe=False)
from bs4 import BeautifulSoup

def fetch_posts_txt(request):
    posts = BlogPost.objects.order_by('-id').all()
    response = []
    for post in posts:
        soup = BeautifulSoup(post.content_html, "html.parser")
        text = ''.join(soup.findAll(text=True)).replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace('  ', ' ')
        response.append({
            'id': post.id,
            'title': post.title,
            'author': post.author,
            'thumbnail': post.thumbnail,
            'content': text,
            'date_created': post.date_created
        })
    return JsonResponse(response, safe=False)















from django.shortcuts import render
from django.http import HttpResponse
from diffusers import StableDiffusionPipeline
from PIL import Image
import cv2
import torch
import os

# Load the model and move it to the GPU
model_loaded = False
image_pipe = None

def load_model():
    global image_pipe, model_loaded
    if not model_loaded:
        image_pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4")
        image_pipe.to("cuda")  # Ensure that CUDA is available and working
        model_loaded = True

def generate_prompts(product_description, background_description):
    image_prompts = [
        f"Show a {product_description} on a {background_description}",
        f"Display a close-up of a {product_description} with a {background_description}",
        f"Show a {product_description} with a {background_description}",
        f"Create an image of a {product_description} on a {background_description}",
        f"Illustrate a {product_description} with a {background_description}"
    ]
    return image_prompts * 2

def generate_images(prompts):
    image_filenames = []
    load_model()

    for i, prompt in enumerate(prompts):
        image = image_pipe(prompt).images[0]
        image_filename = f"media/frame_{i}.png"
        image.save(image_filename)
        image_filenames.append(image_filename)

    return image_filenames

def create_video(image_filenames, video_filename="media/generated_video.mp4", frame_rate=2):
    first_image = cv2.imread(image_filenames[0])
    frame_size = (first_image.shape[1], first_image.shape[0])

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(video_filename, fourcc, frame_rate, frame_size)

    for image_filename in image_filenames:
        frame = cv2.imread(image_filename)
        video_writer.write(frame)

    video_writer.release()

    return video_filename

import os
import uuid
from django.conf import settings
from django.shortcuts import render

def video_generation_view(request):
    if request.method == 'POST':
        product_description = request.POST.get('product_description')
        background_description = request.POST.get('background_description')

        # Generate prompts and images
        prompts = generate_prompts(product_description, background_description)
        image_filenames = generate_images(prompts)

        # Generate the video file and save it to the media/mng/ folder
        video_filename = os.path.join(settings.MEDIA_ROOT, f"generated_video_{uuid.uuid4()}.mp4")

        # Ensure media directory exists before saving video
        os.makedirs(os.path.dirname(video_filename), exist_ok=True)

        # Call the function to create the video
        create_video(image_filenames, video_filename)

        # Check if the video was successfully created
        if os.path.exists(video_filename):
            # Construct the correct video URL to serve the video
            video_url = f"{settings.MEDIA_URL}{os.path.basename(video_filename)}"
            print(f"Video successfully created at {video_filename}")
            print(f"Constructed video URL: {video_url}")
        else:
            video_url = None
            print(f"Video creation failed at {video_filename}")

        return render(request, 'generate_video.html', {'video_url': video_url})

    return render(request, 'generate_video.html')

