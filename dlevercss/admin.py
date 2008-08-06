from django.contrib import admin
from dlevercss.models import Stylesheet

class StylesheetAdmin(admin.ModelAdmin):
    model = Stylesheet
    list_display = ('title', 'filename')

admin.site.register(Stylesheet, StylesheetAdmin)