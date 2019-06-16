from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.views import generic
from django.utils import timezone
from .models import Post, Comment


class IndexView(generic.ListView):
    template_name = 'blog/index.html'
    context_object_name = 'latest_posts_list'

    def get_queryset(self):
        return Post.objects.filter(
          published_date__lte=timezone.now()).order_by('-published_date')


class PostView(generic.DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now())


def leave_a_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    try:
        current_comment = Comment()
        current_comment.text = request.POST['comment_text']
        current_comment.post = post
    except (KeyError, Post.DoesNotExist):
        return render(request, 'blog/detail.html',
                      {'post': post,
                       'error_message': "There's error!(("})
    if not str(current_comment):
        return render(request, 'blog/detail.html',
                      {'post': post,
                       'error_message': "You're motherfucker."})
    else:
        current_comment.save()
        return HttpResponseRedirect(reverse('blog:post_info', args=[post_id]))

