from django import forms
from .models import Page
from .utils import load_page


class PageAdminForm(forms.ModelForm):
#    tmp = load_page(page_name, page_type)
#    content = forms.CharField(widget=forms.Textarea, initial=tmp)

    class Meta:
        fields = "__all__"
        model = Page

