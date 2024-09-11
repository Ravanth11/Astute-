"""
URL configuration for cms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from cms_app import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'blogposts', views.BlogPostViewSet)
urlpatterns = [
     path('login/',views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('sign-up/', views.sign_up_view, name='sign_up'),
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('create/', views.blog_post, name='create'),
    path('blog/<int:id>/', views.get_blog, name='get_blog'),
    path('manage/', views.manage, name='manage'),
    path('view/<int:id>/', views.view_post, name='view_post'),
    path('delete/<int:id>/', views.delete, name='delete'),
    path('edit/<int:id>/', views.update_blog, name='edit_blog'),
    path('upload/', views.upload_image, name='upload_image'),
    path('image/<str:image_uuid>/', views.get_image, name='get_image'),
    path('asset-manager/', views.asset_manager, name='asset_manager'),
    path('delete-image/<int:id>/', views.delete_image, name='delete_image'),
    path('blogs/', views.blog_list, name='blog_list'),
    path('api/',include(router.urls))
]





