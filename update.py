from gedcom.file import GedcomFile
from models import *

from django.utils.datetime_safe import date
from django.utils import timezone
from django.conf import settings
from datetime import datetime
from re import findall
from os import path, mkdir

import Image


def update_from_file(g, file_name, verbose=True):
    lines = open(file_name).read().splitlines()

    update(g, lines, verbose)


def update(g, content, verbose=True):
    if verbose: print 'Parsing content'
    gedcom = GedcomFile(content)  # This is horrible naming.

    if g is None:
        g = Gedcom.objects.create(
            title=gedcom.header.get_child_value_by_tags(
                'TITL', default=''),
            last_updated=datetime(1920, 1, 1)
        )

    if verbose: print 'Importing entries to models'
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

    if verbose:
        print ('Found ' +
           str(person_counter) + ' people, ' +
           str(family_counter) + ' families, ' +
           str(note_counter) + ' notes, and ' +
           str(len(Document.objects.all())) + ' documents.')

    if verbose: print 'Creating ForeignKey links'
    __process_all_relations(g, gedcom, verbose)

    g.last_updated = timezone.now()
    g.save()


#--- Second Level script functions
def __process_all_relations(gedcom_model, gedcom, verbose=True):
    if verbose: print '  Starting Person objects.'
    # Process Person objects
    for person in gedcom_model.person_set.iterator():
        entry = gedcom.get_entry_by_pointer(person.pointer)
        if entry is not None:
            __process_person_relations(gedcom_model, person, entry)
        else:
            person.delete()
    if verbose: print '  Finished Person objects.'
    if verbose: print '  Starting Family objects.'

    # Process Family objects
    for family in gedcom_model.family_set.iterator():
        entry = gedcom.get_entry_by_pointer(family.pointer)
        if entry is not None:
            __process_family_relations(gedcom_model, family, entry)
        else:
            family.delete()
    if verbose: print '  Finished Family objects.'


def __process_person_relations(gedcom, person, entry):
    families = gedcom.family_set
    notes = gedcom.note_set

    # "FAMS"
    person.spousal_families = []
    person.spousal_families.add(*__objects_from_entry_tag(families, entry, 'FAMS'))

    # "FAMC"
    child_family = __objects_from_entry_tag(families, entry, 'FAMC')
    if len(child_family) > 0:
        person.child_family = child_family[0]

    # "NOTE"
    person.notes = []
    person.notes.add(*__objects_from_entry_tag(notes, entry, 'NOTE'))

    person.save()


def __process_family_relations(gedcom, family, entry):
    people = gedcom.person_set
    notes = gedcom.note_set

    # "HUSB"
    family.husbands = []
    family.husbands.add(*__objects_from_entry_tag(people, entry, 'HUSB'))

    # "WIFE"
    family.wives = []
    family.wives.add(*__objects_from_entry_tag(people, entry, 'WIFE'))

    # "CHIL"
    family.children = []
    family.children.add(*__objects_from_entry_tag(people, entry, 'CHIL'))

    # "NOTE"
    family.notes = []
    family.notes.add(*__objects_from_entry_tag(notes, entry, 'NOTE'))

    family.save()


# --- Import Constructors
def __process_Person(entry, g):
    if __check_unchanged(entry, g):
        return

    p, _ = Person.objects.get_or_create(
        pointer=entry.pointer,
        gedcom=g)

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

    # Media
    document_entries = entry.get_children_by_tag('OBJE')
    for m in document_entries:
        try:
            d = __process_Document(m, p, g)
            if (d is not None) & (m.get_child_value_by_tags('PRIM') == 'Y'):
                p.profile.add(d)
        except:
            pass

    p.save()


def __process_Family(entry, g):
    if __check_unchanged(entry, g):
        return

    f, _ = Family.objects.get_or_create(
        pointer=entry.pointer,
        gedcom=g)

    for k in ['MARR', 'DPAR']:
        f.joined = __create_Event(entry.get_child_by_tag(k), g, f.joined)
        if f.joined:
            f.kind = k
            break

    for k in ['DIVF', 'DIVC']:
        f.separated = __create_Event(entry.get_child_by_tag(k), g, f.separated)

    # Media
    document_entries = entry.get_children_by_tag('OBJE')
    for m in document_entries:
        try:
            __process_Document(m, f, g)
        except:
            pass

    f.save()


def __create_Event(entry, g, e):
    if entry is None:
        return None

    (rdate, date_format, 
     year_range_end, date_approxQ) = __parse_gen_date(
        entry.get_child_value_by_tags('DATE'))

    place = entry.get_child_value_by_tags('PLAC', default='')

    if not (date or place):
        return None

    if e is None:
        e = Event(gedcom=g)

    e.date = rdate
    e.place = place
    e.date_format = date_format
    e.year_range_end = year_range_end
    e.date_approxQ = date_approxQ

    e.save()
    return e


def __process_Note(entry, g):
    n, _ = Note.objects.get_or_create(
        pointer=entry.pointer,
        gedcom=g)

    n.text = ''

    for child in entry.children:
        if child.tag == 'CONT':
            n.text += '\n\n' + child.value
        elif child.tag == 'CONC':
            n.text += child.value
    n.text = n.text.strip('\n')

    n.save()

    return n


def __process_Document(entry, object, g):
    if not __valid_document_entry(entry):
        return None

    file_name = __strip_files_directories(entry)
    kind = entry.get_child_value_by_tags('TYPE')

    if kind == 'PHOTO':
        try:
            __make_thumbnail(path.join(settings.MEDIA_ROOT, file_name))
            thumb = path.join('thumbs', file_name)
        except:
            print '  Warning: failed to make or find thumbnail: ' + file_name
            return None  # Bail on document creation if thumb fails

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

    return m


# --- Helper Functions
def __check_unchanged(entry, g):
    changed = __parse_gen_date(
        entry.get_child_value_by_tags(['CHAN', 'DATE']))[0]
    return (changed and g.last_updated and
            (changed <= g.last_updated))


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


def __objects_from_entry_tag(qset, entry, tag):
    pointers = [c.value.strip('@') for c in entry.get_children_by_tag(tag)]
    return list(qset.filter(pointer__in=pointers))


def __valid_document_entry(e):
    file_name = e.get_child_value_by_tags('FILE')
    img_presence = path.join(settings.MEDIA_ROOT, path.basename(file_name))

    return ((type(file_name) is str) &
            (not file_name == '') &
            (path.exists(img_presence)))


def __strip_files_directories(object_entry):
    file_name = object_entry.get_child_value_by_tags('FILE')
    return path.basename(file_name)


def __make_thumbnail(file_name):
    base_name = path.basename(file_name)
    dir_name = path.dirname(file_name)

    thumb_path = path.join(dir_name, 'thumbs')
    thumb_file = path.join(thumb_path, base_name)

    if not path.exists(thumb_path):
        mkdir(thumb_path)  # Worry about permissions?

    size = 150, 150

    if path.exists(thumb_file):
        return thumb_file

    im = Image.open(file_name)
    width, height = im.size

    if width > height:
        offset = (width - height) / 2
        box = (offset, 0, offset + height, height)
    else:
        offset = ((height - width) * 3) / 10
        box = (0, offset, width, offset + width)

    cropped = im.crop(box)
    cropped.thumbnail(size, Image.ANTIALIAS)
    cropped.save(thumb_file)

    return thumb_file
