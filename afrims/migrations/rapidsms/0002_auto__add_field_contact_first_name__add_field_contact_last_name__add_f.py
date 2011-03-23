# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Contact.first_name'
        db.add_column('rapidsms_contact', 'first_name', self.gf('django.db.models.fields.CharField')(default='', max_length=64, blank=True), keep_default=False)

        # Adding field 'Contact.last_name'
        db.add_column('rapidsms_contact', 'last_name', self.gf('django.db.models.fields.CharField')(default='', max_length=64, blank=True), keep_default=False)

        # Adding field 'Contact.email'
        db.add_column('rapidsms_contact', 'email', self.gf('django.db.models.fields.EmailField')(default='', max_length=75, blank=True), keep_default=False)

        # Adding field 'Contact.phone'
        db.add_column('rapidsms_contact', 'phone', self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True), keep_default=False)

        # Adding field 'Contact.title'
        db.add_column('rapidsms_contact', 'title', self.gf('django.db.models.fields.CharField')(default='', max_length=64, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Contact.first_name'
        db.delete_column('rapidsms_contact', 'first_name')

        # Deleting field 'Contact.last_name'
        db.delete_column('rapidsms_contact', 'last_name')

        # Deleting field 'Contact.email'
        db.delete_column('rapidsms_contact', 'email')

        # Deleting field 'Contact.phone'
        db.delete_column('rapidsms_contact', 'phone')

        # Deleting field 'Contact.title'
        db.delete_column('rapidsms_contact', 'title')


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
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'})
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
