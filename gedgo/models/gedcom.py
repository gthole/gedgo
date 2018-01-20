from django.db import models
import random

from person import Person


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
        people = Person.objects.filter(gedcom=self).order_by('?')

        sample = []
        for person in people.iterator():
            if person.key_photo:
                sample.append(person.key_photo)
            if len(sample) == 24:
                break
        return sample
