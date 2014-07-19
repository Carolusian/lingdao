from django.core.urlresolvers import reverse
from mezzanine.blog.models import BlogPost, BlogCategory


class Article(BlogPost):
    class Meta:
        proxy = True

    def get_absolute_url(self):
        url_name = "article-detail"
        kwargs = {"slug" : self.slug}
        return reverse(url_name, kwargs=kwargs)


class ArticleCategory(BlogCategory):
    class Meta:
        proxy = True
