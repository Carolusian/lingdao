from copy import deepcopy

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from mezzanine.conf import settings
from mezzanine.core.admin import DisplayableAdmin, OwnableAdmin
from . import models


articles_fieldsets = deepcopy(DisplayableAdmin.fieldsets)
articles_fieldsets[0][1]["fields"].insert(1, "categories")
articles_fieldsets[0][1]["fields"].extend(["content", "allow_comments"])
articles_list_display = ["title", "user", "status", "admin_link"]
if settings.BLOG_USE_FEATURED_IMAGE:
    articles_fieldsets[0][1]["fields"].insert(-2, "featured_image")
    articles_list_display.insert(0, "admin_thumb")
articles_fieldsets = list(articles_fieldsets)
articles_fieldsets.insert(1, (_("Other posts"), {
    "classes": ("collapse-closed",),
    "fields": ("related_posts",)}))
articles_list_filter = deepcopy(DisplayableAdmin.list_filter) + ("categories",)


class ArticleAdmin(DisplayableAdmin, OwnableAdmin):
    """
    Admin class for blog posts.
    """

    fieldsets = articles_fieldsets
    list_display = articles_list_display
    list_filter = articles_list_filter
    filter_horizontal = ("categories", "related_posts",)

    def save_form(self, request, form, change):
        """
        Super class ordering is important here - user must get saved first.
        """
        OwnableAdmin.save_form(self, request, form, change)
        return DisplayableAdmin.save_form(self, request, form, change)


class ArticleCategoryAdmin(admin.ModelAdmin):
    """
    Admin class for blog categories. Hides itself from the admin menu
    unless explicitly specified.
    """

    fieldsets = ((None, {"fields": ("title",)}),)

    def in_menu(self):
        """
        Hide from the admin menu unless explicitly set in ``ADMIN_MENU_ORDER``.
        """
        for (name, items) in settings.ADMIN_MENU_ORDER:
            if "articles.ArticleCategory" in items:
                return True
        return False


admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.ArticleCategory, ArticleCategoryAdmin)
