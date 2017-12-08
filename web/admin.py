from django.contrib import admin
from .models import Competition, Category, Challenge, Player, SolvedChallenge, Team, Page
from .forms import PageAdminForm



admin.site.register(Competition)
admin.site.register(Category)
admin.site.register(Challenge)
admin.site.register(Player)
admin.site.register(SolvedChallenge)
admin.site.register(Team)
#admin.site.register(Page)

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
#    list_display = ("name", "path", "type", "in_menu","page_content")
#    fields = ("name", "path", "type", "in_menu","page_content")
#
    def page_content(self, obj):
        return obj.page_content()

#    form = PageAdminForm(Path.name, Page.type)
#    fieldsets = (
#    	(None, {
#            'fields': ('name', 'path', 'type', 'in_menu', 'content',),
#        }),
#    )
