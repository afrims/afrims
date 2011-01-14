# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'BroadcastMessage'
        db.create_table('broadcast_broadcastmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(related_name='broadcast_messages', to=orm['rapidsms.Contact'])),
            ('group', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.utcnow)),
            ('logger_message', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['messagelog.Message'], null=True, blank=True)),
        ))
        db.send_create_signal('broadcast', ['BroadcastMessage'])

        # Adding M2M table for field recipients on 'BroadcastMessage'
        db.create_table('broadcast_broadcastmessage_recipients', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('broadcastmessage', models.ForeignKey(orm['broadcast.broadcastmessage'], null=False)),
            ('contact', models.ForeignKey(orm['rapidsms.contact'], null=False))
        ))
        db.create_unique('broadcast_broadcastmessage_recipients', ['broadcastmessage_id', 'contact_id'])

        # Adding model 'BroadcastResponse'
        db.create_table('broadcast_broadcastresponse', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('broadcast', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['broadcast.BroadcastMessage'])),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rapidsms.Contact'])),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.utcnow)),
            ('logger_message', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['messagelog.Message'])),
        ))
        db.send_create_signal('broadcast', ['BroadcastResponse'])


    def backwards(self, orm):
        
        # Deleting model 'BroadcastMessage'
        db.delete_table('broadcast_broadcastmessage')

        # Removing M2M table for field recipients on 'BroadcastMessage'
        db.delete_table('broadcast_broadcastmessage_recipients')

        # Deleting model 'BroadcastResponse'
        db.delete_table('broadcast_broadcastresponse')


    models = {
        'broadcast.broadcastmessage': {
            'Meta': {'object_name': 'BroadcastMessage'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'broadcast_messages'", 'to': "orm['rapidsms.Contact']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logger_message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['messagelog.Message']", 'null': 'True', 'blank': 'True'}),
            'recipients': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'broadcast_messages_received'", 'blank': 'True', 'to': "orm['rapidsms.Contact']"}),
            'text': ('django.db.models.fields.TextField', [], {})
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
