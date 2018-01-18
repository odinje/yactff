from django.contrib import admin
from web.models import Category, Challenge, Submission, Team, Page, User
from django.conf import settings


admin.site.register(Category)
admin.site.register(Challenge)
admin.site.register(Submission)
admin.site.register(User)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        path = "{0}/{1}.{2}".format(settings.PAGE_DIR, obj.name, obj.type)
        with open(path, "w") as f:
            f.write(obj.content)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    readonly_fields=('token',)
