from gedgo.models import Gedcom, BlogPost, Document, Documentary
from django.contrib import admin


class GedcomAdmin(admin.ModelAdmin):
    exclude = ('key_people',)
    filter_horizontal = ('key_families',)


class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "created", "body")
    search_fields = ["title"]
    filter_horizontal = ('tagged_people', 'tagged_photos',)


class DocumentAdmin(admin.ModelAdmin):
    search_fields = ['docfile']
    # Include docfile and kind for uploading new (for blog posts.)
    exclude = ('title', 'description', 'thumb', 'tagged_people',
               'tagged_families', 'gedcom')


class DocumentaryAdmin(admin.ModelAdmin):
    filter_horizontal = ('tagged_people', 'tagged_families',)


admin.site.register(Gedcom, GedcomAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Documentary, DocumentaryAdmin)
