from django.db import models

class Media(models.Model):
	class Meta:
		app_label = 'gedgo'
	name = models.CharField(max_length=40, primary_key=True)
	thumb = models.CharField(max_length=45)
	
	kind = models.CharField(max_length=10)
	
	tagged_people = models.ManyToManyField('Person', related_name='media_tagged_people')
	tagged_families = models.ManyToManyField('Family', related_name='media_tagged_families')
	
	gedcom = models.ForeignKey('Gedcom')
	
	persistent = models.BooleanField()
	
	def key_person_tag(self):
		if self.tagged_people.all():
			return self.tagged_people.all()[0]
	
	def __unicode__(self):
		return self.name + ' (' + self.kind.lower() + ')'