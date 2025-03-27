from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('blogs/', views.BlogListView.as_view(), name='blogs'),
    path('<int:pk>/', views.BlogDetailView.as_view(), name='blog-detail'),
    path('blogger/<int:pk>/', views.BloggerDetailView.as_view(), name='blogger-detail'),
    path('bloggers/', views.BloggerListView.as_view(), name='bloggers'),
    path('<int:pk>/create/', views.CommentCreate.as_view(), name='comment-create'),
    path('register/', views.register, name='register'),
    path('<int:pk>/rate/', views.rate_blog, name='rate-blog'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]