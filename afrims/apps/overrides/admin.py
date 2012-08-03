"Changes to third-party admin registrations."

from django.contrib import admin
from django.core.urlresolvers import reverse

from decisiontree import models

# Change tree registration to be more helpful
admin.site.unregister(models.Tree)
admin.site.unregister(models.Question)
admin.site.unregister(models.TreeState)
admin.site.unregister(models.Answer)
admin.site.unregister(models.Session)
# I don't think we have a need for these so let's not clutter the admin
admin.site.unregister(models.Tag)
admin.site.unregister(models.TagNotification)
# There isn't a good use-case for modifying user's answers
admin.site.unregister(models.Entry)


class TreeAdmin(admin.ModelAdmin):
    "Fancier DecisionTree admin."

    list_display = ('__unicode__', 'trigger', 'root_state', 'report_data', )

    def report_data(self, obj):
        "Link to download the report data."
        url = reverse('export_tree', args=[obj.pk])
        return u"<a href='{0}'>Download Results Report</a>".format(url)
    report_data.allow_tags = True
    report_data.short_description = u"Results Report"


class StateInline(admin.StackedInline):
    "Allow adding a tree state when adding a question."

    model = models.TreeState
    extra = 0


class QuestionAdmin(admin.ModelAdmin):
    "Edit questions with inlines to TreeStates."

    inlines = (StateInline, )


class TransistionInline(admin.StackedInline):
    "Allow adding a transistion when adding an answer."

    model = models.Transition
    extra = 0


class AnswerAdmin(admin.ModelAdmin):
    "Edit answers with inlines to answers."

    list_display = ('name', 'type', 'answer', )
    list_filter = ('type', )
    inlines = (TransistionInline, )


class StateTransistionInline(TransistionInline):
    "Transision has more than FK to state so set fk_name."
    fk_name = 'current_state'


class StateAdmin(admin.ModelAdmin):
    "Edit states with inlines to transisions."
    
    list_display = ('name', 'question', )
    inlines = (StateTransistionInline, )


class SessionAdmin(admin.ModelAdmin):
    "List sessions with better filtering."
    list_display = ('connection', 'tree', 'current_state', 'start_date', 'last_modified', )
    list_filter = ('start_date', 'last_modified', 'tree', )

    def current_state(self, obj):
        "Display current question or note if they have completed the questions."
        return obj.state if obj.state else "completed"
    

admin.site.register(models.Tree, TreeAdmin)
admin.site.register(models.Question, QuestionAdmin)
admin.site.register(models.Answer, AnswerAdmin)
admin.site.register(models.TreeState, StateAdmin)
admin.site.register(models.Session, SessionAdmin)
