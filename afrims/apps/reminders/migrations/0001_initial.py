# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Notification'
        db.create_table('reminders_notification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('num_days', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('reminders', ['Notification'])

        # Adding model 'SentNotification'
        db.create_table('reminders_sentnotification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('notification', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sent_notifications', to=orm['reminders.Notification'])),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sent_notifications', to=orm['rapidsms.Contact'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='queued', max_length=20)),
            ('date_queued', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_delivered', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('date_confirmed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=160)),
        ))
        db.send_create_signal('reminders', ['SentNotification'])

        # Adding model 'PatientDataPayload'
        db.create_table('reminders_patientdatapayload', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('raw_data', self.gf('django.db.models.fields.TextField')()),
            ('submit_date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('reminders', ['PatientDataPayload'])

        # Adding model 'Patient'
        db.create_table('reminders_patient', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('raw_data', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['reminders.PatientDataPayload'], null=True, blank=True)),
            ('subject_number', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('date_enrolled', self.gf('django.db.models.fields.DateField')()),
            ('mobile_number', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('pin', self.gf('django.db.models.fields.CharField')(max_length=4, blank=True)),
            ('next_visit', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rapidsms.Contact'], null=True, blank=True)),
        ))
        db.send_create_signal('reminders', ['Patient'])


    def backwards(self, orm):
        
        # Deleting model 'Notification'
        db.delete_table('reminders_notification')

        # Deleting model 'SentNotification'
        db.delete_table('reminders_sentnotification')

        # Deleting model 'PatientDataPayload'
        db.delete_table('reminders_patientdatapayload')

        # Deleting model 'Patient'
        db.delete_table('reminders_patient')


    models = {
        'rapidsms.contact': {
            'Meta': {'object_name': 'Contact'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'reminders.notification': {
            'Meta': {'object_name': 'Notification'},
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
            'date_delivered': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_queued': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'notification': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_notifications'", 'to': "orm['reminders.Notification']"}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_notifications'", 'to': "orm['rapidsms.Contact']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'queued'", 'max_length': '20'})
        }
    }

    complete_apps = ['reminders']
