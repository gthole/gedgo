from django.db import models
import random

from media import Media
from blogpost import BlogPost
from documentary import Documentary

class Gedcom(models.Model):
	class Meta:
		app_label = 'gedgo'
	file_name = models.CharField(max_length=40, null=True, blank=True)
	title = models.CharField(max_length=40, null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	last_updated = models.DateTimeField()
	
	people = models.ManyToManyField('Person', related_name='gedcom_people')
	families = models.ManyToManyField('Family', related_name='gedcom_families')
	notes = models.ManyToManyField('Note', related_name='gedcom_notes')
	
	key_people = models.ManyToManyField('Person', related_name='gedcom_key_people', null=True, blank=True)
	key_families = models.ManyToManyField('Family', related_name='gedcom_key_families', null=True, blank=True)
	
	def __unicode__(self):
		if self.title is None or self.title == '':
			return 'Gedcom #' + str(self.id)
		else:
			return self.title + ' (' + str(self.id) + ')'
	
	def photo_sample(self):
		photos = Media.objects.filter(gedcom=self, kind='PHOTO')
		return random.sample(photos, min(20, len(photos)))
	
	def showblog(self):
		return True if BlogPost.objects.all() else False
	
	def showdocumentaries(self):
		return True if Documentary.objects.filter(gedcom=self.id) else False