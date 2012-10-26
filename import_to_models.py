from models import Gedcom, Person, Family, Event, Note, Media
from re import findall
from gedcom.file import GedcomFile
from datetime import datetime
import requests
from django.conf import settings

def clear_everything():
	for g in Gedcom.objects.all():
		g.delete()
	print 'Gedcom objects cleared.'
	for p in Person.objects.all():
		p.delete()
	print 'Person objects cleared.'
	for f in Family.objects.all():
		f.delete()
	print 'Family objects cleared.'
	for e in Event.objects.all():
		e.delete()
	print 'Event objects cleared.'
	for n in Note.objects.all():
		n.delete()
	print 'Note objects cleared.'
	for m in Media.objects.all():
		m.delete()
	print 'Media objects cleared.'

def import_to_models(gedcom_file):
	
	print 'Parsing file: ' + gedcom_file
	gedcom = GedcomFile(gedcom_file) # This is horrible naming.
	
	g = Gedcom()

	g.save()
	
	print 'Importing entries to models'
	person_counter = family_counter = note_counter = 0
	for entry in gedcom.entries:
		tag = entry.tag
		
		if tag == 'INDI':
			e = create_Person(entry)
			g.people.add(e)
			person_counter += 1
		elif tag == 'FAM':
			e = create_Family(entry)
			g.families.add(e)
			family_counter += 1
		elif tag == 'NOTE':
			e = create_Note(entry)
			g.notes.add(e)
			note_counter += 1
	
	print ('Found ' + 
		  str(person_counter) + ' people, ' +
		  str(family_counter) + ' families, ' +
		  str(note_counter) + ' notes, and ' + 
		  str(len(Media.objects.all())) + ' photos.')
	
	print 'Creating ForeignKey links'
	process_all_relations(g, gedcom)

def create_Person(entry):
	p = Person()
	p.pointer = entry.pointer
		
	# Name
	name_value = entry.get_child_value_by_tags('NAME', default='')
	name = findall(r'^([^/]*) /([^/]+)/$', name_value)
	if len(name) != 1:
		p.first_name, p.last_name = ('', name_value)
	else:
		p.first_name, p.last_name = name[0]
	p.suffix = entry.get_child_value_by_tags(['NAME', 'NSFX'], default='')
	p.prefix = entry.get_child_value_by_tags(['NAME', 'NPFX'], default='')
	
	p.birth = create_Event(entry.get_child_by_tag('BIRT'))
	p.death = create_Event(entry.get_child_by_tag('DEAT'))
	
	p.save()
	
	# Media
	media_entries = entry.get_children_by_tag('OBJE')
	media_entries = filter(lambda e : __valid_media_entry(e), media_entries)
	for m in media_entries:
		p.media.add(create_Media(m))
	
	p.save()
	
	return p

def create_Family(entry):
	f = Family()
	
	f.pointer = entry.pointer
	
	f.marriage = create_Event(entry.get_child_by_tag('MARR'))
	f.divorce = create_Event(entry.get_child_by_tag('DIVC'))
	
	# Media
	
	f.save()
	
	return f

def create_Event(entry):
	if entry is None:
		return None
	
	e = Event()
	date_results = __parse_gen_date(entry.get_child_value_by_tags('DATE'))
	(e.year_start, e.year_end, e.month, e.day, e.date_approxQ) = date_results
	
	e.place = entry.get_child_value_by_tags('PLAC', default='')
	
	e.save()
	
	return e

def create_Note(entry):
	n = Note()
	
	n.pointer = entry.pointer
	n.text = ''
	
	for child in entry.children:
		if child.tag == 'CONT':
			n.text += '\n\n' + child.value
		elif child.tag == 'CONC':
			n.text += child.value
	n.text = n.text.strip('\n')
	
	n.save()
	
	return n

def create_Media(entry):
	file_name = __strip_files_directories(entry)
	type = entry.get_child_value_by_tags('TYPE')
	
	known = Media.objects.filter(name=file_name)
	
	if len(known) > 0:
		m = known[0]
	else:
		m = Media()
		m.name = file_name
		m.type = type
		m.save()
	
	return m


def __parse_gen_date(date_value):
	if type(date_value) is not str or date_value == '':
		return None, None, None, None, False
	
	date_value = date_value.strip(' ')
	
	# Parse year ranges.
	finds = findall('BET. (\d{4}) - (\d{4})', date_value)
	if len(finds) == 1:
		year_start, year_end = map(lambda x:int(x), finds[0])
		return year_start, year_end, None, None, False
	
	# Parse dates.
	finds = findall('(?:(ABT) +)?(.+)', date_value)
	if len(finds) != 1:
		raise ValueError("Date string not understood: '" + date_value + "'")
	approxQ, date_string = finds[0]
	
	# If 'ABT' is in the date_value, it's an approximate date.
	approxQ = (len(approxQ) > 0)
	
	# Try to parse the date string.
	# TODO: Do this better so it doesn't check all formats.
	# TODO: Factor checked formats out of function.
	year = month = day = None
	try:
		date = datetime.strptime(date_string, '%Y')
		year = date.year
	except ValueError:
		pass
	try:
		date = datetime.strptime(date_string, '%d %b %Y')
		year = date.year
		month = date.month
		day = date.day
	except ValueError:
		pass
	try:
		date = datetime.strptime(date_string, '%b %Y')
		year = date.year
		month = date.month
	except ValueError:
		pass
	
	return year, None, month, day, approxQ


def process_all_relations(gedcom_model, gedcom):
	# Process Person objects
	for person in gedcom_model.people.all():
		entry = gedcom.get_entry_by_pointer(person.pointer)
		if entry is not None:
			process_person_relations(gedcom_model, person, entry)
		else:
			raise ValueError('Cannot find Person with pointer: ' + person.pointer)
	print '  Finished Person objects.'
	
	# Process Family objects
	for family in gedcom_model.families.all():
		entry = gedcom.get_entry_by_pointer(family.pointer)
		if entry is not None:
			process_family_relations(gedcom_model, family, entry)
		else:
			raise ValueError('Cannot find Family with pointer: ' + family.pointer)
	print '  Finished Family objects.'

def process_person_relations(gedcom, person, entry):
	# "FAMS"
	person.spousal_families.add(*objects_from_entry_tag(gedcom.families.all(), entry, 'FAMS'))
	
	# "FAMC"
	child_family = objects_from_entry_tag(gedcom.families.all(), entry, 'FAMC')
	if len(child_family) > 0:
		person.child_family = child_family[0]
	
	# "NOTE"
	person.notes.add(*objects_from_entry_tag(gedcom.notes.all(), entry, 'NOTE'))
		
	person.save()


def process_family_relations(gedcom, family, entry):
	# "HUSB"
	family.husbands.add(*objects_from_entry_tag(gedcom.people.all(), entry, 'HUSB'))
	
	# "WIFE"
	family.wives.add(*objects_from_entry_tag(gedcom.people.all(), entry, 'WIFE'))
	
	# "CHIL"
	family.children.add(*objects_from_entry_tag(gedcom.people.all(), entry, 'CHIL'))

	# "NOTE"
	# family.notes.add(*objects_from_entry_tag(gedcom.notes.all(), entry, 'NOTE'))

	family.save()


def objects_from_entry_tag(objects, entry, tag):
	pointers = map(lambda c : c.value.strip('@'), entry.get_children_by_tag(tag))
	objects = map(lambda pointer : object_from_pointer(objects, pointer), pointers)
	return objects


def object_from_pointer(objects, pointer):
	cand = filter(lambda obj : obj.pointer == pointer, objects)
	
	if len(cand) is not 1:
		raise ValueError('Entry with id ' + pointer + ' is not known.')
	else:
		return cand[0]



def __valid_media_entry(e):
	file_value = e.get_child_value_by_tags('FILE')
	img_presence = requests.head(settings.MEDIA_URL + file_value.split('/')[-1])
	thmb_presence = requests.head(settings.MEDIA_URL + 'thumbs/' + file_value.split('/')[-1])
	return ((e.get_child_value_by_tags('TYPE') == 'PHOTO') & 
		    (type(file_value) is str) & 
		    (not file_value == '') &
			('content-length' in img_presence.headers.keys()) &
			('content-length' in thmb_presence.headers.keys())
		)

def __strip_files_directories(object_entry):
	file_name = object_entry.get_child_value_by_tags('FILE')
	# TODO: Real file name splitting, allow for non-flat directories, search, other operating systems.
	return file_name.split('/')[-1]