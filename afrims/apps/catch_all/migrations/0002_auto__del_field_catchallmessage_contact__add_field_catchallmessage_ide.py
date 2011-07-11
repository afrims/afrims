# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'CatchallMessage.contact'
        db.delete_column('catch_all_catchallmessage', 'contact_id')

        # Adding field 'CatchallMessage.identity'
        db.add_column('catch_all_catchallmessage', 'identity', self.gf('django.db.models.fields.CharField')(default='', max_length=100), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'CatchallMessage.contact'
        db.add_column('catch_all_catchallmessage', 'contact', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['rapidsms.Contact']), keep_default=False)

        # Deleting field 'CatchallMessage.identity'
        db.delete_column('catch_all_catchallmessage', 'identity')


    models = {
        'catch_all.catchallmessage': {
            'Meta': {'object_name': 'CatchallMessage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['catch_all']
