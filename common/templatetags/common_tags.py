# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from future.builtins import str

from collections import defaultdict

from django.template import Context, TemplateSyntaxError, Variable
from django.template.loader import get_template

from mezzanine.pages.models import Page
from mezzanine.blog.models import BlogPost, BlogCategory
from mezzanine.utils.urls import home_slug
from mezzanine import template

from os import path
import settings


register = template.Library()


@register.render_tag
def page_menu_level_2(context, token):
    """
    Return a list of child pages for the given parent, storing all
    pages in a dict in the context when first called using parents as keys
    for retrieval on subsequent recursive calls from the menu template.
    """
    # First arg could be the menu template file name, or the parent page.
    # Also allow for both to be used.
    template_name = None
    parent_page = None
    parts = token.split_contents()[1:]
    for part in parts:
        part = Variable(part).resolve(context)
        if isinstance(part, str):
            template_name = part
        elif isinstance(part, Page):
            parent_page = part
    if template_name is None:
        try:
            template_name = context["menu_template_name"]
        except KeyError:
            error = "No template found for page_menu in: %s" % parts
            raise TemplateSyntaxError(error)
    context["menu_template_name"] = template_name
    if "menu_pages" not in context:
        try:
            user = context["request"].user
            slug = context["request"].path
        except KeyError:
            user = None
            slug = ""
        num_children = lambda id: lambda: len(context["menu_pages"][id])
        has_children = lambda id: lambda: num_children(id)() > 0
        rel = [m.__name__.lower() for m in Page.get_content_models()]
        published = Page.objects.published(for_user=user).select_related(*rel)
        # Store the current page being viewed in the context. Used
        # for comparisons in page.set_menu_helpers.
        if "page" not in context:
            try:
                context["_current_page"] = published.get(slug=slug)
            except Page.DoesNotExist:
                context["_current_page"] = None
        elif slug:
            context["_current_page"] = context["page"]
        # Some homepage related context flags. on_home is just a helper
        # indicated we're on the homepage. has_home indicates an actual
        # page object exists for the homepage, which can be used to
        # determine whether or not to show a hard-coded homepage link
        # in the page menu.
        home = home_slug()
        context["on_home"] = slug == home
        context["has_home"] = False
        # Maintain a dict of page IDs -> parent IDs for fast
        # lookup in setting page.is_current_or_ascendant in
        # page.set_menu_helpers.
        context["_parent_page_ids"] = {}
        pages = defaultdict(list)
        for page in published.order_by("_order"):
            page.set_helpers(context)
            context["_parent_page_ids"][page.id] = page.parent_id
            setattr(page, "num_children", num_children(page.id))
            setattr(page, "has_children", has_children(page.id))
            pages[page.parent_id].append(page)
            if page.slug == home:
                context["has_home"] = True
        context["menu_pages"] = pages
    # ``branch_level`` must be stored against each page so that the
    # calculation of it is correctly applied. This looks weird but if we do
    # the ``branch_level`` as a separate arg to the template tag with the
    # addition performed on it, the addition occurs each time the template
    # tag is called rather than once per level.
    context["branch_level"] = 0
    parent_page_id = None
    if parent_page is not None:
        context["branch_level"] = getattr(parent_page, "branch_level", 0) + 1
        parent_page_id = parent_page.id

    # Build the ``page_branch`` template variable, which is the list of
    # pages for the current parent. Here we also assign the attributes
    # to the page object that determines whether it belongs in the
    # current menu template being rendered.
    context["page_branch"] = context["menu_pages"].get(parent_page_id, [])
    context["page_branch_in_menu"] = False
    for page in context["page_branch"]:
        page.in_menu = page.in_menu_template(template_name)
        page.num_children_in_menu = 0
        if page.in_menu:
            context["page_branch_in_menu"] = True
        for child in context["menu_pages"].get(page.id, []):
            if child.in_menu_template(template_name):
                page.num_children_in_menu += 1
        page.has_children_in_menu = page.num_children_in_menu > 0
        page.branch_level = context["branch_level"]
        page.parent = parent_page
        context["parent_page"] = page.parent

        # Prior to pages having the ``in_menus`` field, pages had two
        # boolean fields ``in_navigation`` and ``in_footer`` for
        # controlling menu inclusion. Attributes and variables
        # simulating these are maintained here for backwards
        # compatibility in templates, but will be removed eventually.
        page.in_navigation = page.in_menu
        page.in_footer = not (not page.in_menu and "footer" in template_name)
        if page.in_navigation:
            context["page_branch_in_navigation"] = True
        if page.in_footer:
            context["page_branch_in_footer"] = True

    # Get its childrens of the current page
    context["children_level_2"] = context["menu_pages"].get(parent_page_id, [])

    t = get_template(template_name)
    return t.render(Context(context))


@register.render_tag
def folding_fan(context, token):
    parts = token.split_contents()[1:]
    fan_name = None
    for part in parts:
        part = Variable(part).resolve(context)
        fan_name = part.strip('/')

    if fan_name.startswith('blog/category/'):
        fan_name = "whatsnew"
    elif fan_name == 'blog':
        fan_name = "whatsnew"

    exist = False
    if fan_name:
        p = path.join(settings.MEDIA_ROOT,
                      'uploads', 'fans', '{0}.png'.format(fan_name))
        exist = path.exists(p)

    context['exist'] = exist
    context['image_url'] = 'media/uploads/fans/{0}.png'.format(fan_name)
    t = get_template("common/menus/fans.html")
    return t.render(Context(context))


@register.render_tag
def page_heading(context, token):
    parts = token.split_contents()[1:]
    heading_name = None
    for part in parts:
        part = Variable(part).resolve(context)
        if isinstance(part, str):
            heading_name = part

    exist = False
    if heading_name:
        p = path.join(settings.MEDIA_ROOT, 'uploads', 'headings',
                      '{0}.png'.format(heading_name))
        exist = path.exists(p)

    context['exist'] = exist
    context['image_url'] = 'media/uploads/headings/{0}.png'.format(heading_name)
    t = get_template("common/menus/headings.html")
    return t.render(Context(context))

@register.render_tag
def index_page_posts(context, token):
    category_name = token.split_contents()[1:2][0]
    category_name = Variable(category_name).resolve(context)

    try:
        category = BlogCategory.objects.get(title__contains=category_name)
        print(category)
        blog_posts = BlogPost.objects.filter(categories=category.pk).order_by('-id')
    except BlogCategory.DoesNotExist:
        blog_posts = []
    
    # Get only the first 10 posts
    context["category"] = category_name
    context["posts"] = blog_posts[0:10]
    t = get_template("common/latest_posts.html")
    return t.render(Context(context))