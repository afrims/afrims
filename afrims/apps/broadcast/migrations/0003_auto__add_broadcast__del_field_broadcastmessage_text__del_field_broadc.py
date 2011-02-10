# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Broadcast'
        db.create_table('broadcast_broadcast', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_last_notified', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('date_next_notified', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('schedule_start_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('schedule_frequency', self.gf('django.db.models.fields.CharField')(default='', max_length=16, blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('broadcast', ['Broadcast'])

        # Adding M2M table for field groups on 'Broadcast'
        db.create_table('broadcast_broadcast_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('broadcast', models.ForeignKey(orm['broadcast.broadcast'], null=False)),
            ('group', models.ForeignKey(orm['reminder.group'], null=False))
        ))
        db.create_unique('broadcast_broadcast_groups', ['broadcast_id', 'group_id'])

        # Deleting field 'BroadcastMessage.text'
        db.delete_column('broadcast_broadcastmessage', 'text')

        # Deleting field 'BroadcastMessage.connection'
        db.delete_column('broadcast_broadcastmessage', 'connection_id')

        # Deleting field 'BroadcastMessage.logger_message'
        db.delete_column('broadcast_broadcastmessage', 'logger_message_id')

        # Deleting field 'BroadcastMessage.date'
        db.delete_column('broadcast_broadcastmessage', 'date')

        # Adding field 'BroadcastMessage.broadcast'
        db.add_column('broadcast_broadcastmessage', 'broadcast', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='messages', to=orm['broadcast.Broadcast']), keep_default=False)

        # Adding field 'BroadcastMessage.recipient'
        db.add_column('broadcast_broadcastmessage', 'recipient', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='broadcast_messages', to=orm['rapidsms.Contact']), keep_default=False)

        # Adding field 'BroadcastMessage.date_created'
        db.add_column('broadcast_broadcastmessage', 'date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.date(2011, 2, 10)), keep_default=False)

        # Adding field 'BroadcastMessage.date_sent'
        db.add_column('broadcast_broadcastmessage', 'date_sent', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True), keep_default=False)

        # Adding field 'BroadcastMessage.status'
        db.add_column('broadcast_broadcastmessage', 'status', self.gf('django.db.models.fields.CharField')(default='queued', max_length=16), keep_default=False)

        # Removing M2M table for field recipients on 'BroadcastMessage'
        db.delete_table('broadcast_broadcastmessage_recipients')


    def backwards(self, orm):
        
        # Deleting model 'Broadcast'
        db.delete_table('broadcast_broadcast')

        # Removing M2M table for field groups on 'Broadcast'
        db.delete_table('broadcast_broadcast_groups')

        # User chose to not deal with backwards NULL issues for 'BroadcastMessage.text'
        raise RuntimeError("Cannot reverse this migration. 'BroadcastMessage.text' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'BroadcastMessage.connection'
        raise RuntimeError("Cannot reverse this migration. 'BroadcastMessage.connection' and its values cannot be restored.")

        # Adding field 'BroadcastMessage.logger_message'
        db.add_column('broadcast_broadcastmessage', 'logger_message', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['messagelog.Message'], null=True, blank=True), keep_default=False)

        # Adding field 'BroadcastMessage.date'
        db.add_column('broadcast_broadcastmessage', 'date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.utcnow), keep_default=False)

        # Deleting field 'BroadcastMessage.broadcast'
        db.delete_column('broadcast_broadcastmessage', 'broadcast_id')

        # Deleting field 'BroadcastMessage.recipient'
        db.delete_column('broadcast_broadcastmessage', 'recipient_id')

        # Deleting field 'BroadcastMessage.date_created'
        db.delete_column('broadcast_broadcastmessage', 'date_created')

        # Deleting field 'BroadcastMessage.date_sent'
        db.delete_column('broadcast_broadcastmessage', 'date_sent')

        # Deleting field 'BroadcastMessage.status'
        db.delete_column('broadcast_broadcastmessage', 'status')

        # Adding M2M table for field recipients on 'BroadcastMessage'
        db.create_table('broadcast_broadcastmessage_recipients', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('broadcastmessage', models.ForeignKey(orm['broadcast.broadcastmessage'], null=False)),
            ('contact', models.ForeignKey(orm['rapidsms.contact'], null=False))
        ))
        db.create_unique('broadcast_broadcastmessage_recipients', ['broadcastmessage_id', 'contact_id'])


    models = {
        'broadcast.broadcast': {
            'Meta': {'object_name': 'Broadcast'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {}),
            'date_last_notified': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'date_next_notified': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'broadcasts'", 'symmetrical': 'False', 'to': "orm['reminder.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'schedule_frequency': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'blank': 'True'}),
            'schedule_start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
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
