from django.db import models
from os import path


class Document(models.Model):
    class Meta:
        app_label = 'gedgo'

    title = models.CharField(max_length=40, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    docfile = models.FileField(upload_to='gedcom')
    last_updated = models.DateTimeField(auto_now_add=True)
    gedcom = models.ForeignKey('Gedcom', null=True, blank=True)

    kind = models.CharField(
        max_length=5,
        choices=(
            ('DOCUM', 'Document'),
            ('VIDEO', 'Video'),
            ('PHOTO', 'Image')
        )
    )
    tagged_people = models.ManyToManyField(
        'Person',
        related_name='media_tagged_people', blank=True
    )
    tagged_families = models.ManyToManyField(
        'Family',
        related_name='media_tagged_families', blank=True
    )

    def __unicode__(self):
        return path.basename(self.docfile.path)

    @property
    def key_person_tag(self):
        if self.tagged_people.exists():
            return self.tagged_people.first()

    @property
    def key_family_tag(self):
        if self.tagged_families.exists():
            return self.tagged_families.first()

    @property
    def file_base_name(self):
        return self.docfile.path.basename()

    @property
    def glyph(self):
        return GLYPH_MAP.get(self.kind) or 'file'


GLYPH_MAP = {
    'DOCUM': 'file',
    'VIDEO': 'facetime-video',
    'PHOTO': 'picture',
    'SOUND': 'volume-up'
}
