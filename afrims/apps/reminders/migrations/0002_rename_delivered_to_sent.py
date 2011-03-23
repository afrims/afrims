# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Renaming field 'SentNotification.date_delivered' to 'date_sent'
        db.rename_column('reminders_sentnotification', 'date_delivered', 'date_sent')

    def backwards(self, orm):
        
        # Renaming field 'SentNotification.date_sent' to 'date_delivered'
        db.rename_column('reminders_sentnotification', 'date_sent', 'date_delivered')

    models = {
        'rapidsms.contact': {
            'Meta': {'object_name': 'Contact'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'reminders.notification': {
            'Meta': {'ordering': "('num_days',)", 'object_name': 'Notification'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_days': ('django.db.models.fields.IntegerField', [], {})
        },
        'reminders.patient': {
            'Meta': {'object_name': 'Patient'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rapidsms.Contact']", 'null': 'True', 'blank': 'True'}),
            'date_enrolled': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile_number': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'next_visit': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'pin': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'}),
            'raw_data': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['reminders.PatientDataPayload']", 'null': 'True', 'blank': 'True'}),
            'subject_number': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'reminders.patientdatapayload': {
            'Meta': {'object_name': 'PatientDataPayload'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'raw_data': ('django.db.models.fields.TextField', [], {}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {})
        },
        'reminders.sentnotification': {
            'Meta': {'object_name': 'SentNotification'},
            'date_confirmed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_queued': ('django.db.models.fields.DateTimeField', [], {}),
            'date_sent': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'notification': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_notifications'", 'to': "orm['reminders.Notification']"}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_notifications'", 'to': "orm['rapidsms.Contact']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'queued'", 'max_length': '20'})
        }
    }

    complete_apps = ['reminders']
