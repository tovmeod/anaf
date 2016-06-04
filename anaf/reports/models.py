"""
Reports models
"""

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from anaf.core.models import Object
from jinja2.filters import do_title
from anaf.reports.helpers import aggregate_functions


class Report(Object):

    """Generated Report"""
    name = models.CharField(max_length=512)
    model = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)

    class Meta:

        """Report"""
        ordering = ['-date_created']

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        """Returns absolute URL for the Report"""
        return reverse('reports_report_view', args=[self.id])


class Model:

    def __init__(self, name='', fields=None):
        self.name = name
        self.fields = fields

    def get_field(self, name):
        for field in self.fields:
            if field.name == name:
                return field
        return None

    def get_class_object(self):
        obj = self.name
        obj = obj.split('.')

        module_name = obj[0] + '.' + obj[1] + '.' + obj[2]
        import_name = obj[3]

        module = __import__(
            module_name, globals(), locals(), [import_name], -1)
        return getattr(module, import_name).objects.all()[0]


class Field:

    def __init__(self, name='', display=False, filters=None, aggregation=None, groupby=0, join=None):
        self.name = name
        self.display = display
        self.filters = [] if filters is None else filters
        self.aggregation = aggregation
        self.groupby = groupby
        self.join = join

    def get_human_name(self):
        """Returns translated name in Camel Case"""
        human = self.name.replace('_', ' ')
        human = _(do_title(human))
        return human

    def get_aggregate_name(self):
        """Returns translated name in Camel Case"""
        if self.aggregation and self.aggregation in aggregate_functions:
            return _(aggregate_functions[self.aggregation]['description'])
        return ''


class Chart(Object):
    name = models.CharField(max_length=255)
    report = models.ForeignKey(Report)
    options = models.TextField(blank=True, null=True)

    access_inherit = ('report', '*module', '*user')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        """Returns absolute URL for the Report"""
        return reverse('reports_report_view', args=[self.report_id])
