from django.shortcuts import get_object_or_404, redirect, render

from . import models


def article_list(request):
    context = {
        "articles": models.Article.objects.order_by("-created_at"),
        "author": None,
    }
    return render(request, "tests/index.html", context)


def user_detail(request, user_id):
    user = get_object_or_404(models.User, pk=user_id)
    context = {
        "articles": models.Article.objects.filter(author=user).order_by("-created_at"),
        "author": user,
    }
    return render(request, "tests/index.html", context)


def article_detail(request, article_pk):
    article = get_object_or_404(models.Article, pk=article_pk)
    comments = models.Comment.objects.filter(article=article).order_by("id")
    token = request.GET.get("token")
    return render(
        request,
        "tests/article.html",
        {"article": article, "comments": comments, "token": token},
    )


def subscriber_detail(request, sub_id):
    subscriber = get_object_or_404(models.Subscriber, pk=sub_id)
    comments = models.Comment.objects.filter(poster=subscriber).order_by("id")
    return render(
        request,
        "tests/subscriber.html",
        {"subscriber": subscriber, "comments": comments},
    )


def comment(request, article_pk):
    token = request.POST.get("token", "")
    content = request.POST.get("content", "")
    article = get_object_or_404(models.Article, pk=article_pk)
    subscriber = models.Subscriber.load_from_token(token)
    models.Comment.objects.create(content=content, poster=subscriber, article=article)
    return redirect("tests:article", article.pk)


def subscribe(request):
    name = request.POST.get("name", "")
    email = request.POST.get("email", "")
    if email == "" or name == "":
        return render(
            request,
            "tests/index.html",
            {"error_message": "You are missing an email or a name"},
        )

    models.Subscriber.objects.create(name=name, email=email)
    return render(request, "tests/subscribed.html")
