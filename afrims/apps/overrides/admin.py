"Changes to third-party admin registrations."

from django.contrib import admin
from django.core.urlresolvers import reverse

from decisiontree import models

# Change tree registration to be more helpful
admin.site.unregister(models.Tree)


class TreeAdmin(admin.ModelAdmin):
    "Fancier DecisionTree admin."

    list_display = ('__unicode__', 'trigger', 'root_state', 'report_data', )

    def report_data(self, obj):
        "Link to download the report data."
        url = reverse('export_tree', args=[obj.pk])
        return u"<a href='{0}'>Download Results Report</a>".format(url)
    report_data.allow_tags = True
    report_data.short_description = u"Results Report"


admin.site.register(models.Tree, TreeAdmin)
