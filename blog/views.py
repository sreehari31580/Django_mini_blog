from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from .models import BlogPost, BlogAuthor, Comment, Rating, ReadingHistory
from django.contrib import messages
from .forms import UserRegisterForm
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import PermissionDenied

# Add this to your existing imports at the top of the file

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_blogs = BlogPost.objects.count()
    num_authors = BlogAuthor.objects.count()
    num_comments = Comment.objects.count()
    
    context = {
        'num_blogs': num_blogs,
        'num_authors': num_authors,
        'num_comments': num_comments,
    }
    
    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BlogListView(generic.ListView):
    """View for listing all blog posts."""
    model = BlogPost
    paginate_by = 5
    template_name = 'blog/blogpost_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get top rated blogs from the past week
        one_week_ago = timezone.now().date() - timedelta(days=7)
        top_rated_blogs = BlogPost.objects.filter(
            ratings__rated_date__gte=one_week_ago
        ).annotate(
            avg_rating=Avg('ratings__rating'),
            num_ratings=Count('ratings')
        ).filter(
            num_ratings__gt=0  # Only include posts with at least one rating
        ).order_by('-avg_rating', '-num_ratings')[:5]

        context['top_rated_blogs'] = top_rated_blogs
        return context

class BlogDetailView(generic.DetailView):
    """View for showing a specific blog post."""
    model = BlogPost
    template_name = 'blog/blogpost_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blog_post = self.get_object()
        
        if self.request.user.is_authenticated:
            # Track that user has read this post
            ReadingHistory.objects.get_or_create(
                user=self.request.user,
                blog_post=blog_post
            )
            
            # Get user's rating for this blog post if it exists
            try:
                user_rating = Rating.objects.get(blog_post=blog_post, user=self.request.user)
                context['user_rating'] = user_rating
            except Rating.DoesNotExist:
                context['user_rating'] = None

        # Get recommended posts
        recommended_posts = self.get_recommended_posts(blog_post)
        context['recommended_posts'] = recommended_posts
        return context
    
    def get_recommended_posts(self, blog_post):
        """Get recommended posts based on various factors."""
        # Get posts by the same author
        author_posts = BlogPost.objects.filter(
            author=blog_post.author
        ).exclude(id=blog_post.id)
        
        # Get posts with similar ratings
        similar_rated_posts = BlogPost.objects.filter(
            ratings__rating__gte=blog_post.average_rating - 0.5,
            ratings__rating__lte=blog_post.average_rating + 0.5
        ).exclude(id=blog_post.id).distinct()
        
        # Get posts read by users who read this post
        if self.request.user.is_authenticated:
            user_recommendations = BlogPost.objects.filter(
                reads__user__in=ReadingHistory.objects.filter(
                    blog_post=blog_post
                ).values_list('user', flat=True)
            ).exclude(id=blog_post.id).distinct()
        else:
            user_recommendations = BlogPost.objects.none()
        
        # Combine and order recommendations
        recommended = list(author_posts[:2])  # 2 posts from same author
        recommended.extend(list(similar_rated_posts.exclude(
            id__in=[p.id for p in recommended]
        )[:2]))  # 2 posts with similar ratings
        recommended.extend(list(user_recommendations.exclude(
            id__in=[p.id for p in recommended]
        )[:2]))  # 2 posts from user behavior
        
        return recommended[:5]  # Return top 5 recommendations

class BloggerListView(generic.ListView):
    """View for listing all bloggers."""
    model = BlogAuthor

class BloggerDetailView(generic.DetailView):
    """View for showing a specific blogger."""
    model = BlogAuthor

class CommentCreate(LoginRequiredMixin, CreateView):
    """View for creating a new comment."""
    model = Comment
    fields = ['description']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blog_post'] = get_object_or_404(BlogPost, pk=self.kwargs['pk'])
        return context
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.blog_post = get_object_or_404(BlogPost, pk=self.kwargs['pk'])
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('blog-detail', kwargs={'pk': self.kwargs['pk']})

@login_required
def rate_blog(request, pk):
    """View to handle blog post rating."""
    blog_post = get_object_or_404(BlogPost, pk=pk)
    
    # Check if user is not an author
    if hasattr(request.user, 'blogauthor'):
        messages.error(request, 'Blog authors cannot rate posts.')
        return redirect('blog-detail', pk=pk)
    
    if request.method == 'POST':
        try:
            rating_value = request.POST.get('rating')
            if not rating_value:
                raise ValueError("Please select a rating")
                
            rating_value = int(rating_value)
            if not 1 <= rating_value <= 5:
                raise ValueError("Rating must be between 1 and 5")
                
            # Update existing rating or create new one
            rating, created = Rating.objects.get_or_create(
                blog_post=blog_post,
                user=request.user,
                defaults={'rating': rating_value}
            )
            
            if not created:
                rating.rating = rating_value
                rating.save()
                
            messages.success(request, 'Your rating has been saved successfully!')
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, 'An error occurred while submitting your rating. Please try again.')
            
    return redirect('blog-detail', pk=pk)