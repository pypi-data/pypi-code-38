import datetime

from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from .models import Post


def create_post(title, text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Post.objects.create(title=title, text=text, published_date=time)


class PostIndexViewTests(TestCase):
    def test_no_posts(self):
        response = self.client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No posts are available.")
        self.assertQuerysetEqual(response.context['latest_posts_list'], [])

    def test_past_post(self):
        create_post(title="Past post.", text="I'm from the past.", days=-30)
        response = self.client.get(reverse('blog:index'))
        self.assertQuerysetEqual(response.context['latest_posts_list'],
                                 ['<Post: Past post.>'])

    def test_future_post(self):
        create_post(title="Future post.", text="I'm from the future.", days=30)
        response = self.client.get(reverse('blog:index'))
        self.assertContains(response, "No posts are available.")
        self.assertQuerysetEqual(response.context['latest_posts_list'], [])

    def test_two_past_posts(self):
        create_post(title='Post 1', text='past', days=-30)
        create_post(title='Post 2', text='past too', days=-5)
        response = self.client.get(reverse('blog:index'))
        self.assertQuerysetEqual(response.context['latest_posts_list'],
                                 ['<Post: Post 2>',
                                  '<Post: Post 1>'])


class PostDetailViewTests(TestCase):
    def test_future_post(self):
        future_post = create_post('Future', "I'm from future.", 5)
        url = reverse('blog:post_info', args=(future_post.id, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_post(self):
        past_post = create_post('Past', "I'm from past.", -5)
        url = reverse('blog:post_info', args=(past_post.id, ))
        response = self.client.get(url)
        self.assertContains(response, past_post.title)


class PostTests(TestCase):

    def test_was_published_recently_with_future_post(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_post = Post()
        future_post.published_date = time

        self.assertIs(future_post.was_published_recently(), False)

    def test_was_published_recently_with_old_post(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_post = Post()
        old_post.published_date = time

        self.assertIs(old_post.was_published_recently(), False)

    def test_was_published_recently_with_recent_post(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_post = Post()
        recent_post.published_date = time

        self.assertIs(recent_post.was_published_recently(), True)


