# -*- coding: utf-8 -*-

from __future__ import absolute_import, with_statement

__all__ = ['TicketStatusHandler', 'ServiceHandler',
           'ServiceLevelAgreementHandler', 'ServiceAgentHandler',
           'TicketQueueHandler', 'TicketRecordHandler', 'TicketHandler']

from anaf.core.api.utils import rc
from piston3.handler import BaseHandler
from anaf.core.models import ModuleSetting
from anaf.core.api.handlers import ObjectHandler
from anaf.services.models import TicketStatus, Service, ServiceLevelAgreement, ServiceAgent, TicketQueue, Ticket, \
    TicketRecord
from anaf.services.forms import TicketForm, TicketStatusForm, TicketRecordForm, QueueForm, \
    ServiceForm, ServiceLevelAgreementForm, AgentForm
from anaf.services.views import _get_default_context


class TicketStatusHandler(ObjectHandler):
    "Entrypoint for TicketStatus model."
    model = TicketStatus
    form = TicketStatusForm

    @classmethod
    def resource_uri(cls, obj=None):
        object_id = "id"
        if obj is not None:
            object_id = obj.id
        return ('api_services_status', [object_id])

    def check_create_permission(self, request, mode):
        return request.user.profile.is_admin('anaf.services')


class ServiceHandler(ObjectHandler):
    "Entrypoint for Service model."
    model = Service
    form = ServiceForm

    @classmethod
    def resource_uri(cls, obj=None):
        object_id = "id"
        if obj is not None:
            object_id = obj.id
        return ('api_services', [object_id])

    def check_create_permission(self, request, mode):
        return request.user.profile.is_admin('anaf.services')

    def check_instance_permission(self, request, inst, mode):
        return request.user.profile.has_permission(inst, mode=mode) \
               or request.user.profile.is_admin('anaf_services')


class ServiceLevelAgreementHandler(ObjectHandler):
    "Entrypoint for ServiceLevelAgreement model."
    model = ServiceLevelAgreement
    form = ServiceLevelAgreementForm

    @classmethod
    def resource_uri(cls, obj=None):
        object_id = "id"
        if obj is not None:
            object_id = obj.id
        return ('api_services_sla', [object_id])

    def check_create_permission(self, request, mode):
        return request.user.profile.is_admin('anaf.services')


class ServiceAgentHandler(ObjectHandler):
    "Entrypoint for ServiceAgent model."
    model = ServiceAgent
    form = AgentForm

    @classmethod
    def resource_uri(cls, obj=None):
        object_id = "id"
        if obj is not None:
            object_id = obj.id
        return ('api_services_agents', [object_id])

    def check_create_permission(self, request, mode):
        return request.user.profile.is_admin('anaf.services')


class TicketQueueHandler(ObjectHandler):
    "Entrypoint for TicketQueue model."
    model = TicketQueue
    form = QueueForm

    @classmethod
    def resource_uri(cls, obj=None):
        object_id = "id"
        if obj is not None:
            object_id = obj.id
        return ('api_services_queues', [object_id])

    def check_create_permission(self, request, mode):
        return request.user.profile.is_admin('anaf.services')


class TicketRecordHandler(BaseHandler):
    "Entrypoint for TicketRecord model."
    model = TicketRecord
    allowed_methods = ('GET', 'POST')
    fields = ('body', 'record_type', 'author', 'comments')

    @classmethod
    def resource_uri(cls, obj=None):
        object_id = "id"
        if obj is not None:
            object_id = obj.id
        return ('api_services_ticket_records', [object_id])

    @staticmethod
    def get_ticket(request, kwargs):
        if 'ticket_id' not in kwargs:
            return rc.BAD_REQUEST
        try:
            ticket = Ticket.objects.get(pk=kwargs['ticket_id'])
        except Ticket.DoesNotExist:
            return rc.NOT_FOUND

        if not request.user.profile.has_permission(ticket):
            return rc.FORBIDDEN
        return ticket

    def read(self, request, *args, **kwargs):
        ticket = self.get_ticket(request, kwargs)

        if isinstance(ticket, Ticket):
            return ticket.updates.all().order_by('date_created')
        else:
            return ticket

    def create(self, request, *args, **kwargs):
        ticket = self.get_ticket(request, kwargs)
        if isinstance(ticket, Ticket):
            profile = request.user.profile
            if profile.has_permission(ticket, mode='w'):
                context = _get_default_context(request)
                agent = context['agent']

                record = TicketRecord(sender=profile.get_contact())
                record.record_type = 'manual'
                if ticket.message:
                    record.message = ticket.message
                form = TicketRecordForm(
                    agent, ticket, request.data, instance=record)
                if form.is_valid():
                    record = form.save()
                    record.save()
                    record.set_user_from_request(request)
                    record.about.add(ticket)
                    ticket.set_last_updated()
                    return record
                else:
                    self.status = 400
                    return form.errors
            else:
                return rc.FORBIDDEN
        else:
            return ticket


class TicketHandler(ObjectHandler):
    "Entrypoint for Ticket model."
    model = Ticket
    form = TicketForm

    @classmethod
    def resource_uri(cls, obj=None):
        object_id = "id"
        if obj is not None:
            object_id = obj.id
        return ('api_services_tickets', [object_id])

    def check_create_permission(self, request, mode):
        request.context = _get_default_context(request)
        request.agent = request.context['agent']
        request.profile = request.user.profile

        request.queue = None
        if 'queue_id' in request.GET:
            try:
                request.queue = TicketQueue.objects.get(
                    pk=request.GET['queue_id'])
            except self.model.DoesNotExist:
                return False
            if not request.user.profile.has_permission(request.queue, mode='w'):
                request.queue = None
        return True

    def check_instance_permission(self, request, inst, mode):
        context = _get_default_context(request)
        request.agent = context['agent']
        request.queue = None
        return request.user.profile.has_permission(inst, mode=mode)

    def flatten_dict(self, request):
        dct = super(TicketHandler, self).flatten_dict(request)
        dct['agent'] = request.agent
        dct['queue'] = request.queue
        return dct

    def create_instance(self, request, *args, **kwargs):
        ticket = Ticket(creator=request.user.profile)
        if not request.agent:
            if request.queue:
                ticket.queue = request.queue
                if request.queue.default_ticket_status:
                    ticket.status = request.queue.default_ticket_status
                else:
                    try:
                        conf = ModuleSetting.get_for_module(
                            'anaf.services', 'default_ticket_status')[0]
                        ticket.status = TicketStatus.objects.get(
                            pk=long(conf.value))
                    except:
                        if 'statuses' in request.context:
                            try:
                                ticket.status = request.context['statuses'][0]
                            except:
                                pass
                ticket.priority = request.queue.default_ticket_priority
                ticket.service = request.queue.default_service
            else:
                try:
                    conf = ModuleSetting.get_for_module(
                        'anaf.services', 'default_ticket_status')[0]
                    ticket.status = TicketStatus.objects.get(
                        pk=long(conf.value))
                except:
                    if 'statuses' in request.context:
                        try:
                            ticket.status = request.context['statuses'][0]
                        except:
                            pass
                try:
                    conf = ModuleSetting.get_for_module(
                        'anaf.services', 'default_ticket_queue')[0]
                    ticket.queue = TicketQueue.objects.get(pk=long(conf.value))
                except:
                    if 'queues' in request.context:
                        try:
                            ticket.queue = request.context['queues'][0]
                        except:
                            pass
            try:
                ticket.caller = request.user.profile.get_contact()
            except:
                pass
        return ticket
