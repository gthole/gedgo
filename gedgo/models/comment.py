from django.db import models
from django.contrib.auth.models import User


class Comment(models.Model):
    class Meta:
        app_label = 'gedgo'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    posted = models.DateTimeField(auto_now_add=True)
    upload = models.FileField(upload_to='uploads/comments', null=True, blank=True)

    gedcom = models.ForeignKey('Gedcom', null=True, blank=True, on_delete=models.CASCADE)
    person = models.ForeignKey('Person', null=True, blank=True, on_delete=models.CASCADE)
    blogpost = models.ForeignKey('BlogPost', null=True, blank=True, on_delete=models.CASCADE)

    @property
    def noun(self):
        if self.blogpost:
            return self.blogpost
        elif self.person:
            return self.person
        return self.gedcom

    def __str__(self):
        return 'Comment about %s by %s (%d)' % (self.noun, self.user, self.id)
