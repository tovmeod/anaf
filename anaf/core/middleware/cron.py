"""
Cron middleware
"""
from anaf.core.conf import settings
from threading import Thread
import time


class CronRunner(Thread):
    """Cron runner"""

    jobs = []
    sleeptime = 60

    def __init__(self, *args, **kwargs):
        "Capture all cron_jobs"
        super(CronRunner, self).__init__(*args, **kwargs)

        self.jobs = []
        self.sleeptime = settings.ANAF_CRON_PERIOD

        for module in settings.INSTALLED_APPS:
            import_name = str(
                module) + "." + settings.ANAF_MODULE_IDENTIFIER
            try:
                hmodule = __import__(import_name, fromlist=[str(module)])
                self.jobs.extend(hmodule.CRON)
            except ImportError:
                pass
            except AttributeError:
                if settings.DEBUG:
                    pass

    def run(self):
        while True:
            for job in self.jobs:
                try:
                    job()
                except:
                    if settings.DEBUG:
                        raise
                    else:
                        import traceback
                        import sys
                        from anaf import core
                        from django.core.mail import mail_admins
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        subject = "Exception: " + \
                            unicode(exc_type) + " " + unicode(exc_value)
                        body = subject + "\n\n"
                        body += unicode(core.__file__) + "\n\n"
                        for s in traceback.format_tb(exc_traceback):
                            body += s + '\n'
                        mail_admins(subject, body)

            time.sleep(self.sleeptime)


class CronMiddleware(object):
    """Cron jobs Middleware"""

    runner = None

    def __init__(self):
        if not settings.ANAF_CRON_DISABLED:
            self.runner = CronRunner()
            self.runner.start()
