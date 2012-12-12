from tastypie.resources import ModelResource
from gedgo.models import Person


class PersonResource(ModelResource):
    class Meta:
        queryset = Person.objects.all()
        resource_name = 'person'