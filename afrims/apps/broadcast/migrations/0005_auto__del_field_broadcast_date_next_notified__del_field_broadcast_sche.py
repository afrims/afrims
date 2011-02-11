# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Broadcast.date_next_notified'
        db.delete_column('broadcast_broadcast', 'date_next_notified')

        # Rename field 'Broadcast.schedule_start_date'
        db.rename_column('broadcast_broadcast', 'schedule_start_date', 'date')

        # Adding unique constraint on 'DateAttribute', fields ['name']
        db.create_unique('broadcast_dateattribute', ['name'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'DateAttribute', fields ['name']
        db.delete_unique('broadcast_dateattribute', ['name'])

        # Adding field 'Broadcast.date_next_notified'
        db.add_column('broadcast_broadcast', 'date_next_notified', self.gf('django.db.models.fields.DateTimeField')(blank=True, null=True, db_index=True), keep_default=False)

        # Rename field 'Broadcast.schedule_start_date'
        db.rename_column('broadcast_broadcast', 'date', 'schedule_start_date')


    models = {
        'broadcast.broadcast': {
            'Meta': {'object_name': 'Broadcast'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {}),
            'date_last_notified': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'broadcasts'", 'symmetrical': 'False', 'to': "orm['reminder.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'months': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'broadcast_months'", 'blank': 'True', 'to': "orm['broadcast.DateAttribute']"}),
            'schedule_end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'schedule_frequency': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'blank': 'True'}),
            'weekdays': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'broadcast_weekdays'", 'blank': 'True', 'to': "orm['broadcast.DateAttribute']"})
        },
        'broadcast.broadcastmessage': {
            'Meta': {'object_name': 'BroadcastMessage'},
            'broadcast': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': "orm['broadcast.Broadcast']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {}),
            'date_sent': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'broadcast_messages'", 'to': "orm['rapidsms.Contact']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'queued'", 'max_length': '16'})
        },
        'broadcast.broadcastresponse': {
            'Meta': {'object_name': 'BroadcastResponse'},
            'broadcast': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['broadcast.BroadcastMessage']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rapidsms.Contact']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logger_message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['messagelog.Message']"}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'broadcast.dateattribute': {
            'Meta': {'ordering': "('value',)", 'unique_together': "(('type', 'value'),)", 'object_name': 'DateAttribute'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'value': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        'messagelog.message': {
            'Meta': {'object_name': 'Message'},
            'connection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rapidsms.Connection']", 'null': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rapidsms.Contact']", 'null': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'rapidsms.backend': {
            'Meta': {'object_name': 'Backend'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        'rapidsms.connection': {
            'Meta': {'unique_together': "(('backend', 'identity'),)", 'object_name': 'Connection'},
            'backend': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rapidsms.Backend']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rapidsms.Contact']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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

    complete_apps = ['broadcast']
