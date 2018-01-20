from django.db import models

from document import Document
from documentary import Documentary


class Family(models.Model):
    class Meta:
        app_label = 'gedgo'
    pointer = models.CharField(max_length=10, primary_key=True)
    gedcom = models.ForeignKey('Gedcom')
    last_changed = models.DateField(null=True, blank=True)

    husbands = models.ManyToManyField('Person', related_name='family_husbands')
    wives = models.ManyToManyField('Person', related_name='family_wives')
    children = models.ManyToManyField('Person', related_name='family_children')

    notes = models.ManyToManyField('Note', blank=True)
    kind = models.CharField('Event', max_length=10, blank=True, null=True)

    joined = models.ForeignKey(
        'Event',
        related_name='family_joined',
        blank=True,
        null=True
    )
    separated = models.ForeignKey(
        'Event',
        related_name='family_separated',
        blank=True,
        null=True
    )

    def __unicode__(self):
        return '%s (%s)' % (self.family_name, self.pointer)

    @property
    def family_name(self):
        nm = ''
        for set in [self.husbands.all(), self.wives.all()]:
            for person in set:
                nm += ' / ' + person.last_name
        return nm.strip(' / ')

    @property
    def single_child(self):
        if self.children.count() == 1:
            return self.children.first()

    @property
    def photos(self):
        return Document.objects.filter(tagged_families=self, kind='PHOTO')

    @property
    def documentaries(self):
        return Documentary.objects.filter(tagged_families=self)

    @property
    def spouses(self):
        for husband in self.husbands.iterator():
            yield husband
        for wife in self.wives.iterator():
            yield wife

    @property
    def ordered_children(self):
        return self.children.order_by('birth__date')
