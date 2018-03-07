from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.core.cache import cache
from web.models import Page
from web.forms import AdminPageForm
from web.decorator import admin_required
from web.utils import random_string, delete_page_file


def page(request, path=None):
    context = {}
    user = request.user
    name = path.split("/")[-1] if path else "index"
    cache_key = "page_{}".format(name)
    page = cache.get(cache_key)
    if not page:
        page = get_object_or_404(Page, name=name)
        cache.set(cache_key, page)
    if user.is_superuser:
        page = get_object_or_404(Page, name=name)  # Need page object for for admin. 
        if request.method == "POST":
            old_name = page.name
            old_type = page.type
            form = AdminPageForm(request.POST, instance=page)
            if form.is_valid():
                page = form.save()
                if old_name != page.name:
                    delete_page_file(old_name, old_type)
                    return redirect("page", path=page.name)
        else:
            form = AdminPageForm(instance=page)
        pages = Page.objects.all()
        template = "web/admin_page.html"
        context["form"] = form
        context["pages"] = pages
    else:
        template = "web/page.html"

    context["page"] = page
    return render(request, template, context)


@admin_required
def page_add(request):
    page_name = random_string()
    try:
        Page.objects.create(name=page_name, content="Text Here")
        return redirect("page", path=page_name)
    except:
        raise Http404  # Change to more useful return code


@admin_required
def page_remove(request, id):
    page = get_object_or_404(Page, id=id)
    if page.name != "index":  # Cannot delete index, maybe give value error?
        page.delete()
    return redirect("index")
