# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'PatientDataPayload.status'
        db.add_column('reminders_patientdatapayload', 'status', self.gf('django.db.models.fields.CharField')(default='queued', max_length=16), keep_default=False)

        # Adding field 'PatientDataPayload.error_message'
        db.add_column('reminders_patientdatapayload', 'error_message', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'PatientDataPayload.status'
        db.delete_column('reminders_patientdatapayload', 'status')

        # Deleting field 'PatientDataPayload.error_message'
        db.delete_column('reminders_patientdatapayload', 'error_message')


    models = {
        'rapidsms.backend': {
            'Meta': {'object_name': 'Backend'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        'rapidsms.contact': {
            'Meta': {'object_name': 'Contact'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'pin': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'primary_backend': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'contact_primary'", 'null': 'True', 'to': "orm['rapidsms.Backend']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'})
        },
        'reminders.notification': {
            'Meta': {'ordering': "('num_days',)", 'object_name': 'Notification'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_days': ('django.db.models.fields.IntegerField', [], {}),
            'recipients': ('django.db.models.fields.CharField', [], {'default': "'all'", 'max_length': '15'}),
            'time_of_day': ('django.db.models.fields.TimeField', [], {})
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
            'error_message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'raw_data': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'queued'", 'max_length': '16'}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {})
        },
        'reminders.sentnotification': {
            'Meta': {'object_name': 'SentNotification'},
            'appt_date': ('django.db.models.fields.DateField', [], {}),
            'date_confirmed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_queued': ('django.db.models.fields.DateTimeField', [], {}),
            'date_sent': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_to_send': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'notification': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_notifications'", 'to': "orm['reminders.Notification']"}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_notifications'", 'to': "orm['rapidsms.Contact']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'queued'", 'max_length': '20'})
        }
    }

    complete_apps = ['reminders']
