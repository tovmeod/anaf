"""
Account cron jobs
"""

import codecs

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.db.models import Q
from django.utils.html import strip_tags
from django.contrib.sites.models import Site

from datetime import datetime, timedelta
from anaf.core.mail import SystemEmail
from anaf.core.models import UpdateRecord
from models import NotificationSetting, Notification


class CronNotifier(object):
    def __init__(self):
        self.next_daily = datetime.now()

    def send_notification(self, note, records):
        message_html = codecs.getwriter("utf8")(StringIO())
        message_html.write(note.title())
        current_url = None
        for record in records:
            if current_url != record.url:
                current_url = record.url
                message_html.write(
                    u'<br /><br />\n\n<a href="{0!s}">'.format(unicode(record.url)))
                if record.sender:
                    message_html.write(u'{0!s}</a> ({1!s}):<br />\n'.format(unicode(record.sender), unicode(record.sender.get_human_type())))
                else:
                    message_html.write(
                        u'{0!s}</a>:<br />\n'.format(unicode(record.url)))
                message_html.write('-' * 30)
                message_html.write('<br /><br />\n\n')
            message_html.write(u'{0!s}:<br />\n{1!s} - {2!s}<br /><br />\n\n'.format(unicode(record.author), unicode(record.date_created.isoformat()),
                                record.get_full_message()))
        signature = "This is an automated message from the Anaf service. Please do not reply to this e-mail."
        subject = "{0!s} summary of [Anaf] {1!s}".format(
            note.get_ntype_display(), unicode(note.owner))

        # send email notification to recipient
        try:
            toaddr = note.owner.get_contact().get_email()
        except:
            toaddr = None
        if toaddr:
            html = message_html.getvalue()
            html = html.replace(
                'href="', 'href="http://' + Site.objects.get_current().domain)
            body = strip_tags(html)
            SystemEmail(
                toaddr, subject, body, signature, html + signature).send_email()
            Notification(
                recipient=note.owner, body=html, ntype=note.ntype).save()

    def send_notifications(self):
        "Run sending some notifications"
        now = datetime.now()

        if self.next_daily <= now:
            notes = NotificationSetting.objects.filter(
                next_date__lte=now.date(), enabled=True)
            for note in notes:
                query = Q()
                for module in note.modules.all():
                    query = query | Q(
                        about__object_type__icontains=module.name)
                query = query & Q(date_created__gte=note.last_datetime) \
                        & (Q(author=note.owner_id) | Q(recipients=note.owner_id))
                self.send_notification(note, UpdateRecord.objects.filter(
                    query).distinct().order_by('url', '-date_created'))
                note.update_date(now)
            self.next_daily = datetime(
                now.year, now.month, now.day) + timedelta(days=1)
