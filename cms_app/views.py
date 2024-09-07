
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

def asset_manager(request):
    images = Images.objects.order_by('-id').all()
    return render(request, 'assets.html', {'images': images, 'user': request.user})

def delete_image(request, id):
    image = get_object_or_404(Images, id=id)
    image.delete()
    messages.success(request, "Image deleted!")
    return redirect('asset_manager')

def blog_list(request):
    posts = BlogPost.objects.all()
    return render(request, 'blog_list.html', {'posts': posts})


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
