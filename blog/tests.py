from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import BlogAuthor, BlogPost, Comment

class BlogAuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user
        test_user = User.objects.create_user(username='testuser', password='12345')
        BlogAuthor.objects.create(user=test_user, bio='This is a test bio')

    def test_bio_label(self):
        author = BlogAuthor.objects.get(id=1)
        field_label = author._meta.get_field('bio').verbose_name
        self.assertEqual(field_label, 'bio')

    def test_bio_max_length(self):
        author = BlogAuthor.objects.get(id=1)
        max_length = author._meta.get_field('bio').max_length
        self.assertEqual(max_length, 1000)

    def test_object_name(self):
        author = BlogAuthor.objects.get(id=1)
        expected_object_name = author.user.username
        self.assertEqual(str(author), expected_object_name)

    def test_get_absolute_url(self):
        author = BlogAuthor.objects.get(id=1)
        self.assertEqual(author.get_absolute_url(), '/blog/blogger/1/')

class BlogPostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user and author
        test_user = User.objects.create_user(username='testuser', password='12345')
        test_author = BlogAuthor.objects.create(user=test_user, bio='This is a test bio')
        
        # Create a test blog post
        BlogPost.objects.create(
            title='Test Blog Post',
            author=test_author,
            content='This is test content for a test blog post.'
        )

    def test_title_label(self):
        blog = BlogPost.objects.get(id=1)
        field_label = blog._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')

    def test_title_max_length(self):
        blog = BlogPost.objects.get(id=1)
        max_length = blog._meta.get_field('title').max_length
        self.assertEqual(max_length, 200)

    def test_content_label(self):
        blog = BlogPost.objects.get(id=1)
        field_label = blog._meta.get_field('content').verbose_name
        self.assertEqual(field_label, 'content')

    def test_content_max_length(self):
        blog = BlogPost.objects.get(id=1)
        max_length = blog._meta.get_field('content').max_length
        self.assertEqual(max_length, 10000)

    def test_object_name(self):
        blog = BlogPost.objects.get(id=1)
        expected_object_name = blog.title
        self.assertEqual(str(blog), expected_object_name)

    def test_get_absolute_url(self):
        blog = BlogPost.objects.get(id=1)
        self.assertEqual(blog.get_absolute_url(), '/blog/1/')

class CommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user, author, and blog post
        test_user = User.objects.create_user(username='testuser', password='12345')
        test_author = BlogAuthor.objects.create(user=test_user, bio='This is a test bio')
        test_blog = BlogPost.objects.create(
            title='Test Blog Post',
            author=test_author,
            content='This is test content for a test blog post.'
        )
        
        # Create a test comment
        Comment.objects.create(
            blog_post=test_blog,
            author=test_user,
            description='This is a test comment.'
        )

    def test_description_label(self):
        comment = Comment.objects.get(id=1)
        field_label = comment._meta.get_field('description').verbose_name
        self.assertEqual(field_label, 'description')

    def test_description_max_length(self):
        comment = Comment.objects.get(id=1)
        max_length = comment._meta.get_field('description').max_length
        self.assertEqual(max_length, 1000)

    def test_object_name(self):
        comment = Comment.objects.get(id=1)
        expected_object_name = f"{comment.description[:75]}..."
        self.assertEqual(str(comment), expected_object_name)

class BlogListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user and author
        test_user = User.objects.create_user(username='testuser', password='12345')
        test_author = BlogAuthor.objects.create(user=test_user, bio='This is a test bio')
        
        # Create 13 test blog posts for pagination tests
        number_of_blogs = 13
        for blog_id in range(number_of_blogs):
            BlogPost.objects.create(
                title=f'Test Blog Post {blog_id}',
                author=test_author,
                content=f'Content for test blog post {blog_id}'
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/blog/blogs/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('blogs'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('blogs'))
        self.assertTemplateUsed(response, 'blog/blogpost_list.html')

    def test_pagination_is_five(self):
        response = self.client.get(reverse('blogs'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['blogpost_list']), 5)