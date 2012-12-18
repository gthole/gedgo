from gedgo.models import Gedcom, Person, BlogPost, Document
from django.contrib import admin

# from djcelery.models import (TaskState, WorkerState,
#		PeriodicTask, IntervalSchedule, CrontabSchedule)


class GedcomAdmin(admin.ModelAdmin):
	exclude = ('people', 'families', 'notes', 'key_people')
	filter_horizontal = ('key_families',)


class BlogPostAdmin(admin.ModelAdmin):
	list_display = ("title", "created", "body")
	search_fields = ["title"]
	filter_horizontal = ('tagged_people', 'tagged_photos',)


class PersonAdmin(admin.ModelAdmin):
	search_fields = ["first_name", "last_name"]
	filter_horizontal = ('profile',)
	exclude = ('pointer', 'gedcom', 'birth', 'death',
			'notes', 'child_family', 'spousal_families',
			'education', 'last_name', 'first_name', 'religion',
			'prefix', 'suffix')


class DocumentAdmin(admin.ModelAdmin):
	search_fields = ['docfile']
	filter_horizontal = ('tagged_people', 'tagged_families',)

admin.site.register(Gedcom, GedcomAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Document, DocumentAdmin)

"""
admin.site.unregister(TaskState)
admin.site.unregister(WorkerState)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(PeriodicTask)
"""
