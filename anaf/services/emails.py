"""
Service Support Emails
"""
from threading import Thread
from anaf.identities.models import ContactValue
from anaf.core.mail import BaseEmail
from django.utils.translation import ugettext as _


class EmailMessage(Thread):
    """Email Message"""

    active = False

    def __init__(self, message, ticket_record):
        Thread.__init__(self)
        self.active = True
        self.message = message
        self.ticket_record = ticket_record

    def run(self):
        "Run"
        self.process_email()

    def send_email(self):
        "Send email"
        self.start()

    def get_original_message_author_email(self):
        "Returns email of the original message author"
        message = self.message
        contact = message.author

        email = ContactValue.objects.filter(
            field__field_type='email', contact=contact)
        if email:
            email = email[0]

        return email

    def get_reply_message_author_email(self):
        "Returns email of the reply message author"
        message = self.message
        contact = message.reply_to.author

        email = ContactValue.objects.filter(
            field__field_type='email', contact=contact)
        if email:
            email = email[0]

        return email

    def process_email(self):
        "Process email"
        message = self.message

        if message.reply_to:
            user = message.reply_to.author.related_user

            original_author = self.get_original_message_author_email()
            reply_author = self.get_reply_message_author_email()

            # if there is no related user and email for message.author
            if not user and original_author and message.stream.outgoing_server_username and reply_author and \
                    message.reply_to.author != message.author:
                # don't send email to yourself

                fromaddr = "{0!s}".format(original_author)
                toaddr = "{0!s}".format(reply_author)

                login = message.stream.outgoing_server_username
                password = message.stream.outgoing_password

                body = self.ticket_record.details + '\r\n\r\n'
                body += _('Your message is received and a ticket is created, ticket reference is [%s]') % (
                    self.ticket_record.ticket.reference)

                subject = "[{0!s}] {1!s}\r\n\r\n".format(
                    self.ticket_record.ticket.reference, self.ticket_record.ticket.message.title)

                BaseEmail(message.stream.outgoing_server_name,
                          login, password, fromaddr, toaddr, subject,
                          body).process_email()
