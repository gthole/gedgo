from django.db import models
from django.utils.datetime_safe import date
from django.conf import settings
from media import Media

class Person(models.Model):
	class Meta:
		app_label = 'gedgo'
		verbose_name_plural = 'People'
	pointer = models.CharField(max_length=10)
	gedcom = models.ForeignKey('Gedcom')
	
	# Name
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=30)	
	prefix = models.CharField(max_length=10)
	suffix = models.CharField(max_length=10)
	
	# Life dates
	birth = models.ForeignKey('Event', related_name='person_birth', null=True, blank=True)
	death = models.ForeignKey('Event', related_name='person_death', null=True, blank=True)
	
	# Details
	education = models.TextField(null=True)
	religion = models.CharField(max_length=50, null=True)
	
	# Family
	child_family = models.ForeignKey('Family', related_name='person_child_family', null=True, blank=True)
	spousal_families = models.ManyToManyField('Family', related_name='person_spousal_families')
	
	# Notes
	notes = models.ManyToManyField('Note', null = True)
	
	# Profile
	profile = models.ManyToManyField('Media', null = True, blank=True)
	
	def photos(self):
		return Media.objects.filter(tagged_people=self, kind='PHOTO')
		
	def videos(self):
		vids = Media.objects.filter(tagged_people=self, kind='VIDEO')
		return filter(lambda v: 'content-length' in requests(v.name).headers.keys(). vids)
		
	def key_photo(self):
		photos = self.photos()
		if photos:
			return photos[len(photos)-1].name
	
	def __unicode__(self):
		return self.last_name + ', ' + self.first_name + ' (' + self.pointer + ')'
	
	def year_range(self):
		if (self.birth is None or self.birth.date is None) and (self.death is None or self.death.date is None):
			return 'unknown'
		return (
			('~' if self.birth is not None and self.birth.date_approxQ else '') +
			(str(self.birth.date.year) if (self.birth is not None and self.birth.date is not None) else ' ') + ' - ' +
			('~' if self.death is not None and self.death.date_approxQ else '') +
			(str(self.death.date.year) if (self.death is not None and self.death.date is not None) else (' ' if self.birth is not None and self.birth.date is not None and self.birth.date.year > 1910 else '?'))
		)
	
	def full_name(self):
		# TODO: Investigate prefix/suffix spacing.
		fn = self.prefix + ' ' + self.first_name + ' ' + self.last_name + ('' if self.suffix == '' or self.suffix[0] == ',' else ' ') + self.suffix
		return fn.strip(' ')
	
	def education_delimited(self):
		if self.education:
			return '\n'.join(self.education.strip(';').split(';'))
		else:
			return ''