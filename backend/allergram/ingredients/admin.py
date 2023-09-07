from django.contrib import admin

from ingredients.models import PhotoQuery


class PhotoQueryAdmin(admin.ModelAdmin):
    pass


admin.site.register(PhotoQuery, PhotoQueryAdmin)
