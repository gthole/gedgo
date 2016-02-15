from django.db import models


class BlogPost(models.Model):
    class Meta:
        app_label = 'gedgo'

    title = models.CharField(max_length=60)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    tagged_photos = models.ManyToManyField(
        'Document',
        related_name='blogpost_tagged_photos',
        blank=True
    )
    tagged_people = models.ManyToManyField(
        'Person',
        related_name='blogpost_tagged_people',
        blank=True
    )

    def __unicode__(self):
        return self.title
