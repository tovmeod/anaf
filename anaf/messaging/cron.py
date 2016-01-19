"""
Cron Job for Messaging module
"""
from models import MessageStream


def process_email():
    """Process email"""
    streams = MessageStream.objects.filter(
        trash=False, incoming_server_username__isnull=False)

    for stream in streams:
        stream.process_email()
