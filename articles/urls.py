# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url
from mezzanine.conf import settings


# Leading and trailing slahes for urlpatterns based on setup.
_slashes = (
    "/" if settings.BLOG_SLUG else "",
    "/" if settings.APPEND_SLASH else "",
)

urlpatterns = patterns(
    "articles.views",
    url("^category/(?P<category>.*)%s$" % _slashes[1],
        'article_list_category',
        name='article-list-category'),
    url("^(?P<slug>.*)%s$" % _slashes[1],
        'article_detail',
        name='article-detail'),
)
