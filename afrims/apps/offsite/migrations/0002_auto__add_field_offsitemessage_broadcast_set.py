# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'OffSiteMessage.broadcast_set'
        db.add_column('offsite_offsitemessage', 'broadcast_set', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'OffSiteMessage.broadcast_set'
        db.delete_column('offsite_offsitemessage', 'broadcast_set')


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
            'broadcast_set': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
