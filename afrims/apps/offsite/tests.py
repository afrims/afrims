# vim: ai ts=4 sts=4 et sw=4
from rapidsms.models import Contact, Connection
from datetime import date,timedelta
from apps.reminder.models import Group 
from apps.offsite import tasks
import time
import unittest
from rapidsms.tests.scripted import TestScript
from apps.offsite.models import HolidayPeriod

class TestApp(TestScript):
    default_group='all_volunteers'

    def create_volunteers(self):
        vNoTravel = self.create_contact('vNoTravel')
        vHasPhone = self.create_contact('vHasPhone')
        vHasAlt = self.create_contact('vHasAlt')
        vNoHasAlt = self.create_contact('vNoHasAlt')
        
    def create_contact(self, name,group=default_group):
        '''
        group keyword argument should be a string (name for the group)
        '''
        ggroup = Group.objects.get_or_create(name=group)[0]
        contact = Contact.objects.create(name=name)
        contact.save()
        contact.groups.add(ggroup)
        script = "%(name)s > hello world" % {"name": name}
        self.runScript(script)
        connection = Connection.objects.get(identity=name)
        connection.contact = contact
        connection.save()
        return contact
    
    def create_test_holiday_and_broadcast(self):

        tasks.create_new_holiday("Test Holiday", (date.today()+timedelta(days=1)), (date.today()+timedelta(days=1)), "Test Holiday Message. Will you be traveling?")
        assert(HolidayPeriod.objects.all()[0].name == "Test Holiday")
#        print 'FFFFFFFFFFFFFUUUUUUUUUUUUUUUU'
        self.runScript("""
        cba1 > hello world
        cba2 > hello world
        """)
        time.sleep(.5)
        self.startRouter()
        tasks.check_for_holiday_and_broadcast(self.router,self.default_group)
        # take a break to allow the router thread to catch up; otherwise we
        # get some bogus messages when they're retrieved below

    
    def test_offsite_kw(self):
        self.startRouter()
        self.create_volunteers()
        self.create_test_holiday_and_broadcast()      




        script="""
        vNoTravel > no
        vNoTravel < Thanks for your response. Enjoy the holidays!
        
        vHasPhone > yes
        vHasPhone < Will you have your phone with you? Please reply with YES or NO
        vHasPhone > yes
        vHasPhone < Please keep your phone with you in case we need to contact you while you are travelling
        
        vHasAlt > yes
        vHasAlt < Will you have your phone with you? Please reply with YES or NO
        vHasAlt > no
        vHasAlt < Do you have an alternative number we can reach you on? Please reply with YES or NO
        vHasAlt > YEs
        vHasAlt < Please contact your Study Clinic to provide them with the alternative number. Hope you have a Merry Christmas!
        
        vNoHasAlt > yes
        vNoHasAlt < Will you have your phone with you? Please reply with YES or NO
        vNoHasAlt > no
        vNoHasAlt < Do you have an alternative number we can reach you on? Please reply with YES or NO
        vNoHasAlt > no
        vNoHasAlt < Please contact the clinic if you notice any fever symptoms while you travel. Have a safe journey!
        
        """
        
        self.runScript(script)
#
#        script="""
#        dho > msg all testing dho blasting
#        """
#        self.runScript(script)
#
#        msgs=self.receiveAllMessages()
#
#        self.assertEqual(3,len(msgs))
#        expected_recipients = ["dho2","clinic_worker","clinic_worker2"]
#        actual_recipients = []
#
#        for msg in msgs:
#            self.assertEqual(msg.text,"testing dho blasting [from dho to ALL]")
#            actual_recipients.append(msg.contact.name)
#        difference = list(set(actual_recipients).difference(set(expected_recipients)))
#        self.assertEqual([], difference)
#
#        script="""
#        dho > msg dho testing dho blasting
#        """
#
#        self.runScript(script)
#        msgs=self.receiveAllMessages()
#
#        # no extra msgs sent
#        self.assertEqual(1, len(msgs))
#        self.assertEqual('dho2', msgs[0].contact.name)
#        self.assertEqual(msgs[0].text, 'testing dho blasting [from dho to DHO]')
#
#        script="""
#        dho > msg clinic testing dho blasting
#        """
#
#        self.runScript(script)
#        msgs=self.receiveAllMessages()
#
#        self.assertEqual(2,len(msgs))
#        expected_recipients = ["clinic_worker","clinic_worker2"]
#        actual_recipients = []
#
#        for msg in msgs:
#            self.assertEqual(msg.text,"testing dho blasting [from dho to CLINIC]")
#            actual_recipients.append(msg.contact.name)
#        difference = list(set(actual_recipients).difference(set(expected_recipients)))
#        self.assertEqual([], difference)

 
        