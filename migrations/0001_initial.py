# -*- coding: utf-8 -*-

from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Document'
        db.create_table('gedgo_document', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('docfile', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('thumb', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('gedcom', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gedgo.Gedcom'], null=True, blank=True)),
        ))
        db.send_create_signal('gedgo', ['Document'])

        # Adding M2M table for field tagged_people on 'Document'
        m2m_table_name = db.shorten_name('gedgo_document_tagged_people')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('document', models.ForeignKey(orm['gedgo.document'], null=False)),
            ('person', models.ForeignKey(orm['gedgo.person'], null=False))
        ))
        db.create_unique(m2m_table_name, ['document_id', 'person_id'])

        # Adding M2M table for field tagged_families on 'Document'
        m2m_table_name = db.shorten_name('gedgo_document_tagged_families')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('document', models.ForeignKey(orm['gedgo.document'], null=False)),
            ('family', models.ForeignKey(orm['gedgo.family'], null=False))
        ))
        db.create_unique(m2m_table_name, ['document_id', 'family_id'])

        # Adding model 'Gedcom'
        db.create_table('gedgo_gedcom', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file_name', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('gedgo', ['Gedcom'])

        # Adding M2M table for field key_people on 'Gedcom'
        m2m_table_name = db.shorten_name('gedgo_gedcom_key_people')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gedcom', models.ForeignKey(orm['gedgo.gedcom'], null=False)),
            ('person', models.ForeignKey(orm['gedgo.person'], null=False))
        ))
        db.create_unique(m2m_table_name, ['gedcom_id', 'person_id'])

        # Adding M2M table for field key_families on 'Gedcom'
        m2m_table_name = db.shorten_name('gedgo_gedcom_key_families')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gedcom', models.ForeignKey(orm['gedgo.gedcom'], null=False)),
            ('family', models.ForeignKey(orm['gedgo.family'], null=False))
        ))
        db.create_unique(m2m_table_name, ['gedcom_id', 'family_id'])

        # Adding model 'Documentary'
        db.create_table('gedgo_documentary', (
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('tagline', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('thumb', self.gf('django.db.models.fields.related.ForeignKey')(related_name='documentaries_thumb', blank=True, to=orm['gedgo.Document'])),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('gedcom', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gedgo.Gedcom'])),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('gedgo', ['Documentary'])

        # Adding M2M table for field tagged_people on 'Documentary'
        m2m_table_name = db.shorten_name('gedgo_documentary_tagged_people')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('documentary', models.ForeignKey(orm['gedgo.documentary'], null=False)),
            ('person', models.ForeignKey(orm['gedgo.person'], null=False))
        ))
        db.create_unique(m2m_table_name, ['documentary_id', 'person_id'])

        # Adding M2M table for field tagged_families on 'Documentary'
        m2m_table_name = db.shorten_name('gedgo_documentary_tagged_families')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('documentary', models.ForeignKey(orm['gedgo.documentary'], null=False)),
            ('family', models.ForeignKey(orm['gedgo.family'], null=False))
        ))
        db.create_unique(m2m_table_name, ['documentary_id', 'family_id'])

        # Adding model 'Person'
        db.create_table('gedgo_person', (
            ('pointer', self.gf('django.db.models.fields.CharField')(max_length=10, primary_key=True)),
            ('gedcom', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gedgo.Gedcom'])),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('prefix', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('suffix', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('birth', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='person_birth', null=True, to=orm['gedgo.Event'])),
            ('death', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='person_death', null=True, to=orm['gedgo.Event'])),
            ('education', self.gf('django.db.models.fields.TextField')(null=True)),
            ('religion', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('child_family', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='person_child_family', null=True, to=orm['gedgo.Family'])),
        ))
        db.send_create_signal('gedgo', ['Person'])

        # Adding M2M table for field spousal_families on 'Person'
        m2m_table_name = db.shorten_name('gedgo_person_spousal_families')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('person', models.ForeignKey(orm['gedgo.person'], null=False)),
            ('family', models.ForeignKey(orm['gedgo.family'], null=False))
        ))
        db.create_unique(m2m_table_name, ['person_id', 'family_id'])

        # Adding M2M table for field notes on 'Person'
        m2m_table_name = db.shorten_name('gedgo_person_notes')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('person', models.ForeignKey(orm['gedgo.person'], null=False)),
            ('note', models.ForeignKey(orm['gedgo.note'], null=False))
        ))
        db.create_unique(m2m_table_name, ['person_id', 'note_id'])

        # Adding M2M table for field profile on 'Person'
        m2m_table_name = db.shorten_name('gedgo_person_profile')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('person', models.ForeignKey(orm['gedgo.person'], null=False)),
            ('document', models.ForeignKey(orm['gedgo.document'], null=False))
        ))
        db.create_unique(m2m_table_name, ['person_id', 'document_id'])

        # Adding model 'Family'
        db.create_table('gedgo_family', (
            ('pointer', self.gf('django.db.models.fields.CharField')(max_length=10, primary_key=True)),
            ('gedcom', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gedgo.Gedcom'])),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('joined', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='family_joined', null=True, to=orm['gedgo.Event'])),
            ('separated', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='family_separated', null=True, to=orm['gedgo.Event'])),
        ))
        db.send_create_signal('gedgo', ['Family'])

        # Adding M2M table for field husbands on 'Family'
        m2m_table_name = db.shorten_name('gedgo_family_husbands')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('family', models.ForeignKey(orm['gedgo.family'], null=False)),
            ('person', models.ForeignKey(orm['gedgo.person'], null=False))
        ))
        db.create_unique(m2m_table_name, ['family_id', 'person_id'])

        # Adding M2M table for field wives on 'Family'
        m2m_table_name = db.shorten_name('gedgo_family_wives')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('family', models.ForeignKey(orm['gedgo.family'], null=False)),
            ('person', models.ForeignKey(orm['gedgo.person'], null=False))
        ))
        db.create_unique(m2m_table_name, ['family_id', 'person_id'])

        # Adding M2M table for field children on 'Family'
        m2m_table_name = db.shorten_name('gedgo_family_children')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('family', models.ForeignKey(orm['gedgo.family'], null=False)),
            ('person', models.ForeignKey(orm['gedgo.person'], null=False))
        ))
        db.create_unique(m2m_table_name, ['family_id', 'person_id'])

        # Adding M2M table for field notes on 'Family'
        m2m_table_name = db.shorten_name('gedgo_family_notes')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('family', models.ForeignKey(orm['gedgo.family'], null=False)),
            ('note', models.ForeignKey(orm['gedgo.note'], null=False))
        ))
        db.create_unique(m2m_table_name, ['family_id', 'note_id'])

        # Adding model 'Event'
        db.create_table('gedgo_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('year_range_end', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('date_format', self.gf('django.db.models.fields.CharField')(max_length=10, null=True)),
            ('date_approxQ', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('gedcom', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gedgo.Gedcom'])),
            ('place', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('gedgo', ['Event'])

        # Adding model 'Note'
        db.create_table('gedgo_note', (
            ('pointer', self.gf('django.db.models.fields.CharField')(max_length=10, primary_key=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('gedcom', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gedgo.Gedcom'])),
        ))
        db.send_create_signal('gedgo', ['Note'])

        # Adding model 'BlogPost'
        db.create_table('gedgo_blogpost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('gedgo', ['BlogPost'])

        # Adding M2M table for field tagged_photos on 'BlogPost'
        m2m_table_name = db.shorten_name('gedgo_blogpost_tagged_photos')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('blogpost', models.ForeignKey(orm['gedgo.blogpost'], null=False)),
            ('document', models.ForeignKey(orm['gedgo.document'], null=False))
        ))
        db.create_unique(m2m_table_name, ['blogpost_id', 'document_id'])

        # Adding M2M table for field tagged_people on 'BlogPost'
        m2m_table_name = db.shorten_name('gedgo_blogpost_tagged_people')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('blogpost', models.ForeignKey(orm['gedgo.blogpost'], null=False)),
            ('person', models.ForeignKey(orm['gedgo.person'], null=False))
        ))
        db.create_unique(m2m_table_name, ['blogpost_id', 'person_id'])

    def backwards(self, orm):
        # Deleting model 'Document'
        db.delete_table('gedgo_document')

        # Removing M2M table for field tagged_people on 'Document'
        db.delete_table(db.shorten_name('gedgo_document_tagged_people'))

        # Removing M2M table for field tagged_families on 'Document'
        db.delete_table(db.shorten_name('gedgo_document_tagged_families'))

        # Deleting model 'Gedcom'
        db.delete_table('gedgo_gedcom')

        # Removing M2M table for field key_people on 'Gedcom'
        db.delete_table(db.shorten_name('gedgo_gedcom_key_people'))

        # Removing M2M table for field key_families on 'Gedcom'
        db.delete_table(db.shorten_name('gedgo_gedcom_key_families'))

        # Deleting model 'Documentary'
        db.delete_table('gedgo_documentary')

        # Removing M2M table for field tagged_people on 'Documentary'
        db.delete_table(db.shorten_name('gedgo_documentary_tagged_people'))

        # Removing M2M table for field tagged_families on 'Documentary'
        db.delete_table(db.shorten_name('gedgo_documentary_tagged_families'))

        # Deleting model 'Person'
        db.delete_table('gedgo_person')

        # Removing M2M table for field spousal_families on 'Person'
        db.delete_table(db.shorten_name('gedgo_person_spousal_families'))

        # Removing M2M table for field notes on 'Person'
        db.delete_table(db.shorten_name('gedgo_person_notes'))

        # Removing M2M table for field profile on 'Person'
        db.delete_table(db.shorten_name('gedgo_person_profile'))

        # Deleting model 'Family'
        db.delete_table('gedgo_family')

        # Removing M2M table for field husbands on 'Family'
        db.delete_table(db.shorten_name('gedgo_family_husbands'))

        # Removing M2M table for field wives on 'Family'
        db.delete_table(db.shorten_name('gedgo_family_wives'))

        # Removing M2M table for field children on 'Family'
        db.delete_table(db.shorten_name('gedgo_family_children'))

        # Removing M2M table for field notes on 'Family'
        db.delete_table(db.shorten_name('gedgo_family_notes'))

        # Deleting model 'Event'
        db.delete_table('gedgo_event')

        # Deleting model 'Note'
        db.delete_table('gedgo_note')

        # Deleting model 'BlogPost'
        db.delete_table('gedgo_blogpost')

        # Removing M2M table for field tagged_photos on 'BlogPost'
        db.delete_table(db.shorten_name('gedgo_blogpost_tagged_photos'))

        # Removing M2M table for field tagged_people on 'BlogPost'
        db.delete_table(db.shorten_name('gedgo_blogpost_tagged_people'))

    models = {
        'gedgo.blogpost': {
            'Meta': {'object_name': 'BlogPost'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tagged_people': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'blogpost_tagged_people'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['gedgo.Person']"}),
            'tagged_photos': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'blogpost_tagged_photos'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['gedgo.Document']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'gedgo.document': {
            'Meta': {'object_name': 'Document'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'docfile': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'gedcom': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gedgo.Gedcom']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'tagged_families': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'media_tagged_families'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['gedgo.Family']"}),
            'tagged_people': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'media_tagged_people'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['gedgo.Person']"}),
            'thumb': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'})
        },
        'gedgo.documentary': {
            'Meta': {'object_name': 'Documentary'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'gedcom': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gedgo.Gedcom']"}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tagged_families': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'documentaries_tagged_families'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['gedgo.Family']"}),
            'tagged_people': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'documentaries_tagged_people'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['gedgo.Person']"}),
            'tagline': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'thumb': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'documentaries_thumb'", 'blank': 'True', 'to': "orm['gedgo.Document']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'})
        },
        'gedgo.event': {
            'Meta': {'object_name': 'Event'},
            'date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'date_approxQ': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date_format': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'gedcom': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gedgo.Gedcom']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'place': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'year_range_end': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'gedgo.family': {
            'Meta': {'object_name': 'Family'},
            'children': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'family_children'", 'symmetrical': 'False', 'to': "orm['gedgo.Person']"}),
            'gedcom': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gedgo.Gedcom']"}),
            'husbands': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'family_husbands'", 'symmetrical': 'False', 'to': "orm['gedgo.Person']"}),
            'joined': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'family_joined'", 'null': 'True', 'to': "orm['gedgo.Event']"}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['gedgo.Note']", 'null': 'True', 'symmetrical': 'False'}),
            'pointer': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'}),
            'separated': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'family_separated'", 'null': 'True', 'to': "orm['gedgo.Event']"}),
            'wives': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'family_wives'", 'symmetrical': 'False', 'to': "orm['gedgo.Person']"})
        },
        'gedgo.gedcom': {
            'Meta': {'object_name': 'Gedcom'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'file_name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key_families': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'gedcom_key_families'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['gedgo.Family']"}),
            'key_people': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'gedcom_key_people'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['gedgo.Person']"}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'})
        },
        'gedgo.note': {
            'Meta': {'object_name': 'Note'},
            'gedcom': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gedgo.Gedcom']"}),
            'pointer': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'gedgo.person': {
            'Meta': {'object_name': 'Person'},
            'birth': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'person_birth'", 'null': 'True', 'to': "orm['gedgo.Event']"}),
            'child_family': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'person_child_family'", 'null': 'True', 'to': "orm['gedgo.Family']"}),
            'death': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'person_death'", 'null': 'True', 'to': "orm['gedgo.Event']"}),
            'education': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'gedcom': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gedgo.Gedcom']"}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'notes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['gedgo.Note']", 'null': 'True', 'symmetrical': 'False'}),
            'pointer': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'profile': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['gedgo.Document']", 'null': 'True', 'blank': 'True'}),
            'religion': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'spousal_families': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'person_spousal_families'", 'symmetrical': 'False', 'to': "orm['gedgo.Family']"}),
            'suffix': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['gedgo']
