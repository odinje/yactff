from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.core.cache import cache
from web.models import Page
from web.forms import AdminPageForm
from web.decorator import admin_required
from web.utils import random_string, delete_page_file
from django.views import View


# https://hackernoon.com/reconciling-djangos-mvc-templates-with-react-components-3aa986cf510a
# https://medium.com/uva-mobile-devhub/set-up-react-in-your-django-project-with-webpack-4fe1f8455396
class PageView(View):
    template = "web/page.html"

    def get(self, request, *args, **kwargs):
        page = get_object_or_404(Page, name="index")
        context = {'page': page}
        return render(request, self.template, context)


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
