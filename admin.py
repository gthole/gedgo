from gedgo.models import Gedcom, Person, BlogPost, Documentary
from django.contrib import admin

class GedcomAdmin(admin.ModelAdmin):
	exclude = ('people', 'families', 'notes', 'key_people')
	filter_horizontal = ('key_families',)


class BlogPostAdmin(admin.ModelAdmin):
	search_fields = ["title"]
	filter_horizontal = ('tagged_people',)

class PersonAdmin(admin.ModelAdmin):
	search_fields = ["first_name", "last_name"]
	exclude = ('pointer', 'gedcom', 'birth', 'death', 
			   'notes', 'child_family', 'spousal_families',
			   'education', 'religion', 'last_name', 'first_name',
			   'prefix', 'suffix')

class DocumentaryAdmin(admin.ModelAdmin):
	exclude = ('gedcom',)
	filter_horizontal = ('tagged_people','tagged_families',)

admin.site.register(Gedcom, GedcomAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Documentary, DocumentaryAdmin)