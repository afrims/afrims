# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Backend'
        db.create_table('rapidsms_backend', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
        ))
        db.send_create_signal('rapidsms', ['Backend'])

        # Adding model 'App'
        db.create_table('rapidsms_app', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('module', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('rapidsms', ['App'])

        # Adding model 'Contact'
        db.create_table('rapidsms_contact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=6, blank=True)),
        ))
        db.send_create_signal('rapidsms', ['Contact'])

        # Adding model 'Connection'
        db.create_table('rapidsms_connection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('backend', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rapidsms.Backend'])),
            ('identity', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rapidsms.Contact'], null=True, blank=True)),
        ))
        db.send_create_signal('rapidsms', ['Connection'])

        # Adding unique constraint on 'Connection', fields ['backend', 'identity']
        db.create_unique('rapidsms_connection', ['backend_id', 'identity'])

        # Adding model 'DeliveryReport'
        db.create_table('rapidsms_deliveryreport', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('report_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('report', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('rapidsms', ['DeliveryReport'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Connection', fields ['backend', 'identity']
        db.delete_unique('rapidsms_connection', ['backend_id', 'identity'])

        # Deleting model 'Backend'
        db.delete_table('rapidsms_backend')

        # Deleting model 'App'
        db.delete_table('rapidsms_app')

        # Deleting model 'Contact'
        db.delete_table('rapidsms_contact')

        # Deleting model 'Connection'
        db.delete_table('rapidsms_connection')

        # Deleting model 'DeliveryReport'
        db.delete_table('rapidsms_deliveryreport')


    models = {
        'rapidsms.app': {
            'Meta': {'object_name': 'App'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'rapidsms.deliveryreport': {
            'Meta': {'object_name': 'DeliveryReport'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'report': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'report_id': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['rapidsms']
