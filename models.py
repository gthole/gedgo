from django.db import models
from datetime import datetime

class Gedcom(models.Model):
	people = models.ManyToManyField('Person')
	families = models.ManyToManyField('Family')
	notes = models.ManyToManyField('Note')

class Person(models.Model):
	pointer = models.CharField(max_length=10)
	
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=30)	
	prefix = models.CharField(max_length=10)
	suffix = models.CharField(max_length=10)
	
	birth = models.ForeignKey('Event', related_name='person_birth', null=True, blank=True)
	death = models.ForeignKey('Event', related_name='person_death', null=True, blank=True)
	
	# Family
	child_family = models.ForeignKey('Family', related_name='person_child_family', null=True, blank=True)
	spousal_families = models.ManyToManyField('Family', related_name='person_spousal_families')
	
	# Notes
	notes = models.ManyToManyField('Note', null = True)
	
	# Media
	media = models.ManyToManyField('Media')
	
	def key_photo(self):
		if self.media.all():
			return self.media.all()[0].name
	
	def __unicode__(self):
		return self.last_name + ', ' + self.first_name + ' (' + self.pointer + ')'
	
	def year_range(self):
		if self.birth is None or self.birth.year_start is None:
			return 'unknown'
		return (('~' if self.birth is not None and self.birth.date_approxQ else '') + 
				str(self.birth.year_start) + 
				' - ' + 
				('~' if ((self.death is not None) and (self.death.date_approxQ)) else '') + 
				(str(self.death.year_start) if self.death is not None else (' ' if self.birth.year_start > 1920 else '?')))
	
	def full_name(self):
		# TODO: Investigate prefix/suffix spacing.
		fn = self.prefix + ' ' + self.first_name + ' ' + self.last_name + self.suffix
		return fn.strip(' ')


class Family(models.Model):
	pointer = models.CharField(max_length=10)
	
	husbands = models.ManyToManyField('Person', related_name='family_husbands')
	wives = models.ManyToManyField('Person', related_name='family_wives')
	children = models.ManyToManyField('Person', related_name='family_children')
	
	marriage = models.ForeignKey('Event', related_name='family_marriage', blank=True, null=True)
	divorce = models.ForeignKey('Event', related_name='family_divorce', blank=True, null=True)
	
	# Notes
	# notes = models.ManyToManyField('Note', null = True)
	
	def single_child(self):
		if len(self.children.all()) == 1:
			return self.children.all()[0]


class Event(models.Model):
	# Can't use DateFields because sometimes only a Year is known, and we don't want
	# to show those as January 01, <year>, and datetime doesn't allow missing values.
	year_start = models.IntegerField(null = True)
	year_end = models.IntegerField(null = True)
	month = models.IntegerField(null = True)
	day = models.IntegerField(null = True)
	date_approxQ = models.BooleanField('Date is approximate')
	
	place = models.CharField(max_length=50)
	
	# Breaks strict MVC conventions.
	def date_string(self):
		if self.year_start is None:
			return ''
		elif self.year_end:
			return 'between ' + str(self.year_start) + ' and ' + str(self.year_end)
		elif self.month is None:
			date_format = ''
			month = day = 1
		elif self.day is None:
			date_format = '%B '
			month = self.month
			day = 1
		else:
			month = self.month
			day = self.day
			date_format = '%B %d, '
		# strftime doesn't work before 1900?
		return datetime(1900, month, day).strftime(date_format) + str(self.year_start)

class Note(models.Model):
	pointer = models.CharField(max_length=10)
	
	text = models.TextField()
	def br_text(self):
		return self.text.replace('\n','<br>')

class Media(models.Model):
	name = models.CharField(max_length=40, primary_key=True)
	
	type = models.CharField(max_length=10)
	