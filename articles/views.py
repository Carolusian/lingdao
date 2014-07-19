# -*- coding: utf-8 -*-
"""
   This articles app is designed specifically for use caes in lingdao.hk
   It is based on mezzanine.blog app
"""

from django.shortcuts import render, get_object_or_404
from .models import ArticleCategory, Article


def article_list_category(request, category):
    category = get_object_or_404(ArticleCategory, slug=category)
    articles = Article.objects.published(for_user=request.user)
    articles = articles.filter(categories=category)

    context = {'category': category, 'articles': articles}
    return render(
        request,
        "articles/article_list_category.html", context)


def article_detail(request, slug):
    articles = Article.objects.published(for_user=request.user).select_related()
    article = get_object_or_404(articles, slug=slug)
    context = {'article': article, 'editable_obj': article}
    return render(request, "articles/article_detail.html", context)
