from mezzanine.blog.models import BlogPost, BlogCategory


class Article(BlogPost):
    class Meta:
        proxy = True


class ArticleCategory(BlogCategory):
    class Meta:
        proxy = True
