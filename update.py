from gedcom.file import GedcomFile
from models import *

from django.utils.datetime_safe import date
from django.utils import timezone
from django.conf import settings
from datetime import datetime
from re import findall
from os import path


def update_from_file(g, file_name):
	# TODO: Fix \r or \n issue.
	lines = open(file_name).read().split("\r")

	update(g, lines)


def update(g, content):
	print 'Parsing content'
	gedcom = GedcomFile(content)  # This is horrible naming.

	if g is None:
		g = Gedcom()
		g.title = gedcom.header.get_child_value_by_tags('TITL', default='')
		g.last_updated = timezone.now()
	else:
		g.last_updated = timezone.now()

	g.save()

	print 'Importing entries to models'
	person_counter = family_counter = note_counter = 0
	for entry in gedcom.entries:
		tag = entry.tag

		if tag == 'INDI':
			__process_Person(entry, g)
			person_counter += 1
		elif tag == 'FAM':
			__process_Family(entry, g)
			family_counter += 1
		elif tag == 'NOTE':
			__process_Note(entry, g)
			note_counter += 1

	print ('Found ' +
			str(person_counter) + ' people, ' +
			str(family_counter) + ' families, ' +
			str(note_counter) + ' notes, and ' +
			str(len(Document.objects.all())) + ' documents.')

	print 'Creating ForeignKey links'
	__process_all_relations(g, gedcom)


#--- Second Level script functions
def __process_all_relations(gedcom_model, gedcom):
	# Process Person objects
	for person in gedcom_model.people.all():
		entry = gedcom.get_entry_by_pointer(person.pointer)
		if entry is not None:
			__process_person_relations(gedcom_model, person, entry)
		else:
			raise ValueError('Cannot find Person with pointer: ' + person.pointer)
	print '  Finished Person objects.'

	# Process Family objects
	for family in gedcom_model.families.all():
		entry = gedcom.get_entry_by_pointer(family.pointer)
		if entry is not None:
			__process_family_relations(gedcom_model, family, entry)
		else:
			raise ValueError('Cannot find Family with pointer: ' + family.pointer)
	print '  Finished Family objects.'


def __process_person_relations(gedcom, person, entry):
	# "FAMS"
	person.spousal_families = []
	person.spousal_families.add(*__objects_from_entry_tag(gedcom.families.all(), entry, 'FAMS'))

	# "FAMC"
	child_family = __objects_from_entry_tag(gedcom.families.all(), entry, 'FAMC')
	if len(child_family) > 0:
		person.child_family = child_family[0]

	# "NOTE"
	person.notes = []
	person.notes.add(*__objects_from_entry_tag(gedcom.notes.all(), entry, 'NOTE'))

	person.save()


def __process_family_relations(gedcom, family, entry):
	# "HUSB"
	family.husbands = []
	family.husbands.add(*__objects_from_entry_tag(gedcom.people.all(), entry, 'HUSB'))

	# "WIFE"
	family.wives = []
	family.wives.add(*__objects_from_entry_tag(gedcom.people.all(), entry, 'WIFE'))

	# "CHIL"
	family.children = []
	family.children.add(*__objects_from_entry_tag(gedcom.people.all(), entry, 'CHIL'))

	# "NOTE"
	family.notes = []
	family.notes.add(*__objects_from_entry_tag(gedcom.notes.all(), entry, 'NOTE'))

	family.save()


# --- Import Constructors
def __process_Person(entry, g):
	known = Person.objects.filter(pointer=entry.pointer)

	if len(known) == 0:
		p = Person()
		p.pointer = entry.pointer
		p.gedcom = g
		g.people.add(p)
	else:
		p = known[0]

	# Name
	name_value = entry.get_child_value_by_tags('NAME', default='')
	name = findall(r'^([^/]*) /([^/]+)/$', name_value)
	if len(name) != 1:
		p.first_name, p.last_name = ('', name_value)
	else:
		p.first_name, p.last_name = name[0]
	p.suffix = entry.get_child_value_by_tags(['NAME', 'NSFX'], default='')
	p.prefix = entry.get_child_value_by_tags(['NAME', 'NPFX'], default='')

	p.birth = __create_Event(entry.get_child_by_tag('BIRT'), g, p.birth)
	p.death = __create_Event(entry.get_child_by_tag('DEAT'), g, p.death)

	p.education = entry.get_child_value_by_tags('EDUC')
	p.religion = entry.get_child_value_by_tags('RELI')

	p.save()

	# Media
	document_entries = entry.get_children_by_tag('OBJE')
	for m in document_entries:
		__process_Document(m, p, g)

	return p


def __process_Family(entry, g):
	known = Family.objects.filter(pointer=entry.pointer)

	if len(known) == 0:
		f = Family()
	else:
		f = known[0]

	f.pointer = entry.pointer
	f.gedcom = g

	f.marriage = __create_Event(entry.get_child_by_tag('MARR'), g, f.marriage)
	f.divorce = __create_Event(entry.get_child_by_tag('DIVC'), g, f.divorce)

	f.save()

	# Media
	document_entries = entry.get_children_by_tag('OBJE')
	for m in document_entries:
		__process_Document(m, f, g)

	f.save()

	g.families.add(f)

	return f


def __create_Event(entry, g, e):
	if entry is None:
		return None
	
	date_results = __parse_gen_date(entry.get_child_value_by_tags('DATE'))
	(rdate, date_format, year_range_end, date_approxQ) = date_results
	
	place = entry.get_child_value_by_tags('PLAC', default='')
	
	if not (date or place):
		return None
	
	if e is None:
		e = Event()
		e.gedcom = g

	e.date = rdate
	e.place = place
	e.date_format = date_format
	e.year_range_end = year_range_end
	e.date_approxQ = date_approxQ
	
	e.save()
	return e


def __process_Note(entry, g):
	known = Note.objects.filter(pointer=entry.pointer)
	
	if len(known) == 0:
		n = Note()
	else:
		n = known[0]
	
	n.pointer = entry.pointer
	n.gedcom = g
	n.text = ''
	
	for child in entry.children:
		if child.tag == 'CONT':
			n.text += '\n\n' + child.value
		elif child.tag == 'CONC':
			n.text += child.value
	n.text = n.text.strip('\n')
	
	n.save()
	
	g.notes.add(n)
	
	return n


def __process_Document(entry, object, g):
	if not __valid_document_entry(entry):
		return None
	
	file_name = __strip_files_directories(entry)
	kind = entry.get_child_value_by_tags('TYPE')
	if kind == 'PHOTO':
		thumb = 'thumbs/' + file_name  # TODO: Fix for non-Linux
	else:
		thumb = None
	
	known = Document.objects.filter(docfile=unicode(file_name))
	
	if len(known) > 0:
		m = known[0]
	else:
		m = Document(gedcom=g, kind=kind)
		m.docfile.name = file_name
		if thumb is not None:
			m.thumb.name = thumb
		m.save()
	
	if (type(object) is Person) & (len(m.tagged_people.filter(pointer=object.pointer)) == 0):
		m.tagged_people.add(object)
	elif (type(object) is Family) & (len(m.tagged_families.filter(pointer=object.pointer)) == 0):
		m.tagged_families.add(object)


# --- Helper Functions
DATE_FORMATS = [
	('%Y', '%Y'),
	('%d %b %Y', '%B %d, %Y'),
	('%b %Y', '%B, %Y')
]


def __parse_gen_date(date_value):
	if type(date_value) is not str or date_value == '':
		return None, None, None, False
	
	date_value = date_value.strip(' ')
	
	# Parse year ranges.
	finds = findall('BET. (\d{4}) - (\d{4})', date_value)
	if len(finds) == 1:
		year, year_range_end = map(lambda x: int(x), finds[0])
		return datetime(year, 1, 1), '%Y', year_range_end, False
	
	# Parse dates.
	finds = findall('(?:(ABT) +)?(.+)', date_value)
	if len(finds) != 1:
		raise ValueError("Date string not understood: '" + date_value + "'")
	approxQ, date_string = finds[0]
	
	# If 'ABT' is in the date_value, it's an approximate date.
	approxQ = (len(approxQ) > 0)
	
	# Try to parse the date string.
	rdate = None
	for date_format in DATE_FORMATS:
		try:
			rdate = datetime.strptime(date_string, date_format[0])
			break
		except ValueError:
			pass
	if rdate is None:
		return None, None, None, False
		#raise ValueError("Could not parse date string: '" + date_value + "'")
	
	return date(rdate.year, rdate.month, rdate.day), date_format[1], None, approxQ


def __objects_from_entry_tag(objects, entry, tag):
	pointers = map(lambda c: c.value.strip('@'), entry.get_children_by_tag(tag))
	objects = map(lambda pointer: __object_from_pointer(objects, pointer), pointers)
	return objects


def __object_from_pointer(objects, pointer):
	cand = filter(lambda obj: obj.pointer == pointer, objects)
	
	if len(cand) is not 1:
		raise ValueError('Entry with id ' + pointer + ' is not known.')
	else:
		return cand[0]


def __valid_document_entry(e):
	# TODO: Fix Windows issues.
	file_value = e.get_child_value_by_tags('FILE')
	img_presence = settings.MEDIA_ROOT + path.basename(file_value)
	thmb_presence = settings.MEDIA_ROOT + path.join('thumbs', path.basename(file_value))
	return ((type(file_value) is str) &
			(not file_value == '') &
			(path.exists(img_presence)) &
			((e.get_child_value_by_tags('TYPE') != 'PHOTO') |
				(path.exists(thmb_presence)))
		)


def __strip_files_directories(object_entry):
	file_name = object_entry.get_child_value_by_tags('FILE')
	# TODO: Real file name splitting, allow for non-flat directories, search, other operating systems.
	return file_name.split('/')[-1]
