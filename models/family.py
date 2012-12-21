from django.db import models

from document import Document
from documentary import Documentary


class Family(models.Model):
	class Meta:
		app_label = 'gedgo'
	pointer = models.CharField(max_length=10, primary_key=True)
	gedcom = models.ForeignKey('Gedcom')

	husbands = models.ManyToManyField('Person', related_name='family_husbands')
	wives = models.ManyToManyField('Person', related_name='family_wives')
	children = models.ManyToManyField('Person', related_name='family_children')

	marriage = models.ForeignKey('Event', related_name='family_marriage', blank=True, null=True)
	divorce = models.ForeignKey('Event', related_name='family_divorce', blank=True, null=True)

	notes = models.ManyToManyField('Note', null=True)

	def family_name(self):
		nm = ''
		for set in [self.husbands.all(), self.wives.all()]:
			for person in set:
				nm += ' / ' + person.last_name
		return nm.strip(' / ')

	def __unicode__(self):
		txt = self.family_name()
		return (txt + ' (' + self.pointer + ')')

	def single_child(self):
		if len(self.children.all()) == 1:
			return self.children.all()[0]

	def photos(self):
		return Document.objects.filter(tagged_families=self, kind='PHOTO')

	def documentaries(self):
		return Documentary.objects.filter(tagged_families=self)
