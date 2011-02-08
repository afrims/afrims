# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'HolidayPeriod'
        db.create_table('offsite_holidayperiod', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('travel_message', self.gf('django.db.models.fields.CharField')(max_length=160)),
        ))
        db.send_create_signal('offsite', ['HolidayPeriod'])

        # Adding model 'OffSiteMessage'
        db.create_table('offsite_offsitemessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rapidsms.Contact'])),
            ('holiday', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['offsite.HolidayPeriod'])),
            ('message_status', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('offsite', ['OffSiteMessage'])


    def backwards(self, orm):
        
        # Deleting model 'HolidayPeriod'
        db.delete_table('offsite_holidayperiod')

        # Deleting model 'OffSiteMessage'
        db.delete_table('offsite_offsitemessage')


    models = {
        'offsite.holidayperiod': {
            'Meta': {'object_name': 'HolidayPeriod'},
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'travel_message': ('django.db.models.fields.CharField', [], {'max_length': '160'})
        },
        'offsite.offsitemessage': {
            'Meta': {'object_name': 'OffSiteMessage'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rapidsms.Contact']"}),
            'holiday': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['offsite.HolidayPeriod']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_status': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'rapidsms.contact': {
            'Meta': {'object_name': 'Contact'},
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['reminder.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'reminder.group': {
            'Meta': {'object_name': 'Group'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['offsite']
