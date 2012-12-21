from tastypie.resources import ModelResource
from gedgo.models import Person


class PersonResource(ModelResource):
	class Meta:
		list_allowed_methods = ['get']
		queryset = Person.objects.all()
		resource_name = 'person'

	def dehydrate(self, bundle):
		photos = bundle.obj.photos()
		if not photos:
			return bundle
		images = map(lambda i: i.docfile.url, photos)
		bundle.data['images'] = images
		return bundle
