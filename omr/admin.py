from django.contrib import admin

from omr.models import File, Author


class FileAdmin(admin.ModelAdmin):
    search_fields = ['model', 'author']
    list_display = ['model', 'author', 'alternate_model', 'missing_parts', 'missing_patterns', 'missing_stickers']
    list_filter = ['is_main_model', 'missing_parts', 'missing_patterns', 'missing_stickers']


class AuthorAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name', 'nickname']
    list_display = ['first_name', 'last_name', 'nickname']


admin.site.register(File, FileAdmin)
admin.site.register(Author, AuthorAdmin)

admin.site.site_header = 'LDraw OMR Administration'
admin.site.site_title = 'LDraw OMR'
admin.site.index_title = 'Administration'
