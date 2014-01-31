from django.db import models
from django.utils.datetime_safe import date


class Event(models.Model):
    class Meta:
        app_label = 'gedgo'
    # Can't use DateFields because sometimes only a Year is known, and
    # we don't want to show those as January 01, <year>, and datetime
    # doesn't allow missing values.
    date = models.DateField(null=True)
    year_range_end = models.IntegerField(null=True)
    date_format = models.CharField(null=True, max_length=10)
    date_approxQ = models.BooleanField('Date is approximate')
    gedcom = models.ForeignKey('Gedcom')
    place = models.CharField(max_length=50)

    # Breaks strict MVC conventions.
    # Hack around python datetime's 1900 limitation.
    def date_string(self):
        if self.date is None:
            return ''
        elif self.year_range_end:
            return 'between %d and %d' % (self.date.year, self.year_range_end)
        elif self.date_format:
            new_date = date(self.date.year, self.date.month, self.date.day)
            return new_date.strftime(self.date_format)

    def __unicode__(self):
        return self.date_string + ' (' + self.id + ')'
