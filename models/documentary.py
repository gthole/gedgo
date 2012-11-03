from django.db import models

class Documentary(models.Model):
	class Meta:
		app_label = 'gedgo'
		verbose_name_plural = 'Documentaries'
	title = models.CharField(max_length=40, primary_key=True)
	
	location = models.CharField(max_length=45, null=True, blank=True)
	thumb = models.CharField(max_length=45, null=True, blank=True)
	
	description = models.TextField(null=True, blank=True)
	
	last_updated = models.DateTimeField(auto_now_add=True)
	
	tagged_people = models.ManyToManyField('Person', related_name='documentaries_tagged_people', null=True, blank=True)
	tagged_families = models.ManyToManyField('Family', related_name='documentaries_tagged_families', null=True, blank=True)
	
	gedcom = models.ForeignKey('Gedcom')
	
	def __unicode__(self):
		return self.title