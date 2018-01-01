from django.contrib import admin
from .models import Category, Challenge, SolvedChallenge, Team, Page, User
from django.conf import settings


admin.site.register(Category)
admin.site.register(Challenge)
admin.site.register(SolvedChallenge)
admin.site.register(Team)
admin.site.register(User)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        path = "{0}/{1}.{2}".format(settings.PAGE_DIR, obj.name, obj.type)
        with open(path, "w") as f:
            f.write(obj.content)
