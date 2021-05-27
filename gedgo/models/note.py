from django.db import models


class Note(models.Model):
    class Meta:
        app_label = 'gedgo'
    pointer = models.CharField(max_length=10, primary_key=True)
    text = models.TextField()
    gedcom = models.ForeignKey('Gedcom', on_delete=models.CASCADE)

    def __str__(self):
        return 'Note (%s)' % self.pointer

    @property
    def br_text(self):
        return self.text.replace('\n', '<br>')
