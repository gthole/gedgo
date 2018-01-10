from gedcom_parser import GedcomParser
from models import Gedcom, Person, Family, Note, Document, Event

from django.core.files.storage import default_storage
from django.db import transaction
from django.utils.datetime_safe import date
from django.utils import timezone
from datetime import datetime
from re import findall
from os import path
from cStringIO import StringIO

from PIL import Image

from gedgo.storages import gedcom_storage


@transaction.atomic
def update(g, file_name, verbose=True):
    # Prevent circular dependencies
    if verbose:
        print 'Parsing content'
    parsed = GedcomParser(file_name)

    if g is None:
        g = Gedcom.objects.create(
            title=__child_value_by_tags(parsed.header, 'TITL', default=''),
            last_updated=datetime(1920, 1, 1)  # TODO: Fix.
        )
    print g.id

    if verbose:
        print 'Importing entries to models'
    person_counter = family_counter = note_counter = 0
    entries = parsed.entries.values()
    for index, entry in enumerate(entries):
        tag = entry['tag']

        if tag == 'INDI':
            __process_Person(entry, g)
            person_counter += 1
        elif tag == 'FAM':
            __process_Family(entry, g)
            family_counter += 1
        elif tag == 'NOTE':
            __process_Note(entry, g)
            note_counter += 1

        if (index + 1) % 100 == 0:
            print ' ... %d / %d' % (index + 1, len(entries))

    if verbose:
        print 'Found %d people, %d families, %d notes, and %d documents' % (
            person_counter, family_counter, note_counter,
            Document.objects.count())

    if verbose:
        print 'Creating ForeignKey links'

    __process_all_relations(g, parsed, verbose)

    g.last_updated = timezone.now()
    g.save()


# --- Second Level script functions
def __process_all_relations(gedcom, parsed, verbose=True):
    if verbose:
        print '  Starting Person objects.'

    # Process Person objects
    for index, person in enumerate(gedcom.person_set.iterator()):
        entry = parsed.entries.get(person.pointer)
        print index
        if entry is not None:
            __process_person_relations(gedcom, person, entry)
        else:
            person.delete()
    if verbose:
        print '  Finished Person objects, starting Family objects.'

    # Process Family objects
    for family in gedcom.family_set.iterator():
        entry = parsed.entries.get(family.pointer)

        if entry is not None:
            __process_family_relations(gedcom, family, entry)
        else:
            family.delete()
    if verbose:
        print '  Finished Family objects.'


def __process_person_relations(gedcom, person, entry):
    families = gedcom.family_set
    notes = gedcom.note_set

    # "FAMS"
    person.spousal_families = []
    person.spousal_families.add(
        *__objects_from_entry_tag(families, entry, 'FAMS')
    )

    # "FAMC"
    person.child_family = None
    child_family = __objects_from_entry_tag(families, entry, 'FAMC')
    if child_family:
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
        pointer=entry['pointer'],
        gedcom=g)

    # Name
    name_value = __child_value_by_tags(entry, 'NAME', default='')
    name = findall(r'^([^/]*) /([^/]+)/$', name_value)
    if len(name) != 1:
        p.first_name, p.last_name = ('', name_value)
    else:
        p.first_name, p.last_name = name[0]
    p.suffix = __child_value_by_tags(entry, ['NAME', 'NSFX'], default='')
    p.prefix = __child_value_by_tags(entry, ['NAME', 'NPFX'], default='')

    p.birth = __create_Event(__child_by_tag(entry, 'BIRT'), g, p.birth)
    p.death = __create_Event(__child_by_tag(entry, 'DEAT'), g, p.death)

    p.education = __child_value_by_tags(entry, 'EDUC')
    p.religion = __child_value_by_tags(entry, 'RELI')

    # Media
    document_entries = [
        c for c in entry.get('children', [])
        if c['tag'] == 'OBJE'
    ]
    for m in document_entries:
        d = __process_Document(m, p, g)
        if (d is not None) and (__child_value_by_tags(m, 'PRIM') == 'Y'):
            p.profile.add(d)

    p.save()


def __process_Family(entry, g):
    if __check_unchanged(entry, g):
        return

    f, _ = Family.objects.get_or_create(
        pointer=entry['pointer'],
        gedcom=g)

    for k in ['MARR', 'DPAR']:
        f.joined = __create_Event(__child_by_tag(entry, k), g, f.joined)
        if f.joined:
            f.kind = k
            break

    for k in ['DIVF', 'DIVC']:
        f.separated = __create_Event(__child_by_tag(entry, k), g, f.separated)

    # Media
    document_entries = [
        c for c in entry.get('children', [])
        if c['tag'] == 'OBJE'
    ]
    for m in document_entries:
        __process_Document(m, f, g)

    f.save()


def __create_Event(entry, g, e):
    if entry is None:
        return None

    (rdate, date_format, year_range_end, date_approxQ) = __parse_gen_date(
        __child_value_by_tags(entry, 'DATE'))

    place = __child_value_by_tags(entry, 'PLAC', default='')

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
        pointer=entry['pointer'],
        gedcom=g)

    n.text = ''

    for child in entry.get('children', []):
        if child['tag'] == 'CONT':
            n.text += '\n\n%s' % child.get('value', '')
        elif child['tag'] == 'CONC':
            n.text += child.get('value', '')
    n.text = n.text.strip('\n')

    n.save()
    return n


def __process_Document(entry, obj, g):
    name = __valid_document_entry(entry)
    if not name:
        return None

    file_name = 'gedcom/%s' % name
    known = Document.objects.filter(docfile=file_name)

    if len(known) > 0:
        m = known[0]
    else:
        kind = __child_value_by_tags(entry, 'TYPE')
        m = Document(gedcom=g, kind=kind)
        m.docfile.name = file_name
        if kind == 'PHOTO':
            try:
                make_thumbnail(name, __child_value_by_tags(entry, 'CROP'))
                thumb = path.join('default/thumbs', name)
            except:
                print '  Warning: failed to make or find thumbnail: %s' % name
                return None  # Bail on document creation if thumb fails
        else:
            thumb = None
        if thumb is not None:
            m.thumb.name = thumb
        m.save()

    if isinstance(obj, Person) and \
            not m.tagged_people.filter(pointer=obj.pointer).exists():
        m.tagged_people.add(obj)
    elif isinstance(obj, Family) and \
            not m.tagged_families.filter(pointer=obj.pointer).exists():
        m.tagged_families.add(obj)

    return m


# --- Helper Functions
def __check_unchanged(entry, g):
    changed = __parse_gen_date(
        __child_value_by_tags(entry, ['CHAN', 'DATE'])
    )[0]
    return changed and g.last_updated and (changed <= g.last_updated)


DATE_FORMATS = [
    ('%Y', '%Y'),
    ('%d %b %Y', '%B %d, %Y'),
    ('%b %Y', '%B, %Y')
]


# TODO: Clean up this dreadful function
def __parse_gen_date(date_value):
    if type(date_value) is not str or date_value == '':
        return None, None, None, False

    date_value = date_value.strip(' ')

    # Parse year ranges.
    found = findall(r'^BET. (\d{4}) - (\d{4})$', date_value)
    if found:
        year, year_range_end = [int(y) for y in found[0]]
        return datetime(year, 1, 1), '%Y', year_range_end, False

    # Parse dates.
    found = findall(r'^(?:(ABT) +)?(.+)$', date_value)
    if not found:
        raise ValueError("Date string not understood: '%s'" % date_value)
    approxQ, date_string = found[0]

    # If 'ABT' is in the date_value, it's an approximate date.
    approxQ = (len(approxQ) > 0)

    # Try to parse the date string.
    rdate = None
    for parse_format, print_format in DATE_FORMATS:
        try:
            rdate = datetime.strptime(date_string, parse_format)
            return (
                date(rdate.year, rdate.month, rdate.day),
                print_format, None, approxQ
            )
        except ValueError:
            pass
    return None, None, None, False


def __objects_from_entry_tag(qset, entry, tag):
    pointers = [
        c['value'].strip('@') for c in entry.get('children', [])
        if c['tag'] == tag
    ]
    return list(qset.filter(pointer__in=pointers))


def __child_value_by_tags(entry, tags, default=None):
    if isinstance(tags, basestring):
        tags = [tags]
    tags.reverse()
    next = entry
    while tags and isinstance(next, dict):
        tag = tags.pop()
        next = __child_by_tag(next, tag)
        if next is None:
            return default
    return next.get('value', default)


def __child_by_tag(entry, tag):
    for child in entry.get('children', []):
        if child['tag'] == tag:
            return child


def __valid_document_entry(e):
    full_name = __child_value_by_tags(e, 'FILE')
    name = path.basename(full_name).decode('utf-8').strip()
    if gedcom_storage.exists(name):
        return name


def make_thumbnail(name, crop):
    """
    Copies an image from gedcom_storage, converts it to a thumbnail, and saves
    it to default_storage for fast access
    """
    thumb_name = path.join('thumbs', name)

    if default_storage.exists(thumb_name):
        return thumb_name

    im = Image.open(gedcom_storage.open(name))
    width, height = im.size

    # TODO: Use crop argument
    if width > height:
        offset = (width - height) / 2
        box = (offset, 0, offset + height, height)
    else:
        offset = ((height - width) * 3) / 10
        box = (0, offset, width, offset + width)
    cropped = im.crop(box)

    size = 150, 150
    cropped.thumbnail(size, Image.ANTIALIAS)
    output = StringIO()
    cropped.save(output, 'JPEG')
    return default_storage.save(thumb_name, output)
