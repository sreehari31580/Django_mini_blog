# Create your models here.
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta

class BlogAuthor(models.Model):
    """Model representing a blog author (blogger)."""
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    bio = models.TextField(max_length=1000, help_text="Enter a brief bio about yourself.")
    
    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse('blogger-detail', args=[str(self.id)])
    
    def __str__(self):
        """String representation of the model object."""
        return self.user.username

class BlogPost(models.Model):
    """Model representing a blog post."""
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(BlogAuthor, on_delete=models.SET_NULL, null=True)
    post_date = models.DateField(auto_now_add=True)

    @property
    def average_rating(self):
        """Calculate the average rating for this blog post."""
        avg = self.ratings.aggregate(Avg('rating'))['rating__avg']
        return avg if avg is not None else 0

    @property
    def total_ratings(self):
        """Get the total number of ratings for this blog post."""
        return self.ratings.count()

    class Meta:
        ordering = ['-post_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog-detail', args=[str(self.id)])

class Comment(models.Model):
    """Model representing a comment on a blog post."""
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    post_date = models.DateField(auto_now_add=True)
    description = models.TextField(max_length=1000, help_text="Enter your comment here.")
    
    class Meta:
        ordering = ['post_date']  # Sort by post date in ascending order
    
    def __str__(self):
        """String representation of the model object."""
        return f"{self.description[:75]}..."  # Truncate to 75 characters

class Rating(models.Model):
    """Model representing a rating on a blog post."""
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 rating
    rated_date = models.DateField(auto_now_add=True)
    
    class Meta:
        # Ensure a user can only rate a blog post once
        unique_together = ['blog_post', 'user']
        ordering = ['-rated_date']
    
    def __str__(self):
        return f"{self.user.username}'s {self.rating}-star rating on {self.blog_post.title}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Check if the user is not an author
        if hasattr(self.user, 'blogauthor'):
            raise ValidationError("Blog authors cannot rate posts.")

class ReadingHistory(models.Model):
    """Model to track which posts users have read."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_history')
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='reads')
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-read_at']
        unique_together = ['user', 'blog_post']

    def __str__(self):
        return f"{self.user.username} read {self.blog_post.title}"