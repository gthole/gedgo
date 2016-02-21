from django.db import models
import random

from document import Document


class Gedcom(models.Model):
    class Meta:
        app_label = 'gedgo'

    file_name = models.CharField(max_length=40, null=True, blank=True)
    title = models.CharField(max_length=40, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    last_updated = models.DateTimeField()

    key_people = models.ManyToManyField(
        'Person',
        related_name='gedcom_key_people',
        blank=True
    )
    key_families = models.ManyToManyField(
        'Family',
        related_name='gedcom_key_families',
        blank=True
    )

    def __unicode__(self):
        if not self.title:
            return 'Gedcom #%d' % self.id
        return '%s (%d)' % (self.title, self.id)

    @property
    def photo_sample(self):
        photos = Document.objects.filter(gedcom=self, kind='PHOTO')
        return random.sample(photos, min(24, len(photos)))
