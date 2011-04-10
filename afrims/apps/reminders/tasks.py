from threadless_router.router import Router

from celery.task import Task
from celery.registry import tasks

from afrims.apps.reminders.app import scheduler_callback, daily_email_callback


class ReminderSchedulerTask(Task):
    def run(self):
        router = Router()
        scheduler_callback(router)


tasks.register(ReminderSchedulerTask)


class ReminderEmailTask(Task):
    def run(self):
        router = Router()
        daily_email_callback(router)


tasks.register(ReminderEmailTask)
