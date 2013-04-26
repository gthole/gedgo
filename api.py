from tastypie.resources import ModelResource
from gedgo.models import Person, Family
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import ReadOnlyAuthorization

from functools import wraps


def add_photos(f):
    @wraps(f)
    def wrapper(self, bundle):
        photos = bundle.obj.photos()
        if not photos:
            return bundle
        images = map(lambda i: i.docfile.url, photos)
        bundle.data['images'] = images
        return bundle
    return wrapper


class PersonResource(ModelResource):
    class Meta:
        list_allowed_methods = ['get']
        queryset = Person.objects.all()
        resource_name = 'person'
        authentication = BasicAuthentication()
        authorization = ReadOnlyAuthorization()

    @add_photos
    def dehydrate(self, bundle):
        return bundle


class FamilyResource(ModelResource):
    class Meta:
        list_allowed_methods = ['get']
        queryset = Family.objects.all()
        resource_name = 'family'
        authentication = BasicAuthentication()
        authorization = ReadOnlyAuthorization()

    @add_photos
    def dehydrate(self, bundle):
        return bundle
