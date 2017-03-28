from __future__ import absolute_import

from django.utils.module_loading import import_string

from openduty.celery import app

from notification.models import ScheduledNotification
from django.conf import settings
from django.utils import timezone

from openduty.models import EventLog


@app.task(ignore_result=True)
def send_notifications(notification_id):
    try:
        notification = ScheduledNotification.objects.get(id=notification_id)
    except ScheduledNotification.DoesNotExist:
        return  # Incident was resolved. NOP.

    try:
        notifier_class = import_string(
            "{}.Notifier".format(notification.notifier))
    except ImportError:
        return

    notifier_settings = getattr(settings, notifier_class.settings_name, {})
    notifier = notifier_class(notifier_settings)
    try:
        notifier.notify(notification)
    except:
        # Log successful notification
        logmessage = EventLog()
        if notification.incident:
            logmessage.service_key = notification.incident.service_key
            logmessage.incident_key = notification.incident
            logmessage.user = notification.user_to_notify
            logmessage.action = 'notification_failed'
            logmessage.data = "Sending notification failed to %s about %s " \
                              "service" % (
            notification.user_to_notify, logmessage.service_key,)
            logmessage.occurred_at = timezone.now()
            logmessage.save()
        raise
    else:
        logmessage = EventLog()
        if notification.incident:
            logmessage.service_key = notification.incident.service_key
            logmessage.incident_key = notification.incident
            logmessage.user = notification.user_to_notify
            logmessage.action = 'notified'
            logmessage.data = "Notification sent to %s about %s service" % (
                notification.user_to_notify, logmessage.service_key,)
            logmessage.occurred_at = timezone.now()
            logmessage.save()
        if notifier.delete_on_send:
            notification.delete()
