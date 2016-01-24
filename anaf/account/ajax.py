"""
Core Ajax views
"""

from django.template import RequestContext
import re
from anaf.core.mail import EmailInvitation
from django.contrib.sites.models import RequestSite
from anaf.core.models import Attachment, Invitation
from anaf.core.views import user_denied
from anaf.core.rendering import render_to_string
from anaf.core.models import Comment, Object, UpdateRecord, Tag
from anaf.core.forms import TagsForm
from anaf.core.ajax import converter
from dajaxice.core import dajaxice_functions
from dajax.core import Dajax


def comments_likes(request, target, form, expand=True):
    dajax = Dajax()

    response_format = 'html'

    object_id = form.get('object_id', 0)
    update = form.get('update', 0)
    if update:
        obj = UpdateRecord.objects.get(pk=object_id)
    else:
        obj = Object.objects.get(pk=object_id)

    profile = request.user.profile

    if obj:
        if form.get('like', 0) == unicode(obj.id):
            obj.likes.add(profile)
            if hasattr(obj, 'score'):
                obj.score += 1
                obj.save()

        elif form.get('unlike', 0) == unicode(obj.id):
            obj.likes.remove(profile)
            if hasattr(obj, 'score'):
                obj.score -= 1
                obj.save()

        elif form.get('dislike', 0) == unicode(obj.id):
            obj.dislikes.add(profile)
            if hasattr(obj, 'score'):
                obj.score += 1
                obj.save()

        elif form.get('undislike', 0) == unicode(obj.id):
            obj.dislikes.remove(profile)
            if hasattr(obj, 'score'):
                obj.score -= 1
                obj.save()

        elif form.get('commentobject', 0) == unicode(obj.id) and 'comment' in form:
            comment = Comment(author=profile,
                              body=form.get('comment'))
            comment.save()
            if hasattr(obj, 'score'):
                obj.score += 1
                obj.save()
            obj.comments.add(comment)

    likes = obj.likes.all()
    dislikes = obj.dislikes.all()
    comments = obj.comments.all()

    ilike = profile in likes
    idislike = profile in dislikes
    icommented = comments.filter(author=profile).exists() or \
        comments.filter(author__default_group__in=[
                        profile.default_group_id] + [i.id for i in profile.other_groups.all().only('id')]).exists()

    output = render_to_string('core/tags/comments_likes',
                              {'object': obj,
                               'is_update': update,
                               'profile': profile,
                               'likes': likes,
                               'dislikes': dislikes,
                               'comments': comments,
                               'ilike': ilike,
                               'idislike': idislike,
                               'icommented': icommented,
                               'expand': expand},
                              context_instance=RequestContext(request),
                              response_format=response_format)

    dajax.add_data({'target': target, 'content': output}, 'anaf.add_data')
    return dajax.json()

dajaxice_functions.register(comments_likes)


def tags(request, target, object_id, edit=False, formdata=None):
    if formdata is None:
        formdata = {}
    dajax = Dajax()

    response_format = 'html'
    obj = Object.objects.get(pk=object_id)

    tags = obj.tags.all()
    form = None
    if 'tags' in formdata and not type(formdata['tags']) == list:
        formdata['tags'] = [formdata['tags']]

    if edit or formdata:
        if formdata.get('tags_object', 0) == unicode(obj.id):
            form = TagsForm(tags, formdata)
            if form.is_valid():
                if 'multicomplete_tags' in formdata:
                    tag_names = formdata.get('multicomplete_tags').split(',')
                    new_tags = []
                    for name in tag_names:
                        name = name.strip()
                        if name:
                            try:
                                tag = Tag.objects.get(name=name)
                            except Tag.DoesNotExist:
                                tag = Tag(name=name)
                                tag.save()
                            new_tags.append(tag)
                else:
                    new_tags = form.is_valid()

                obj.tags.clear()
                for tag in new_tags:
                    obj.tags.add(tag)
                tags = obj.tags.all()
                form = None
        else:
            form = TagsForm(tags)

    context = {'object': obj,
               'tags': tags,
               'form': form}

    context = converter.preprocess_context(context)

    output = render_to_string('core/ajax/tags_box', context,
                              context_instance=RequestContext(request),
                              response_format=response_format)

    dajax.add_data({'target': target, 'content': output}, 'anaf.add_data')
    return dajax.json()

dajaxice_functions.register(tags)


def attachment(request, object_id, update_id=None):
    dajax = Dajax()

    try:

        if object_id:
            attachments = Attachment.objects.filter(
                attached_object__id=object_id)
            template = 'core/tags/attachments_block'

            object_markup = render_to_string(template,
                                             {'object_id': object_id,
                                                 'attachments': attachments},
                                             context_instance=RequestContext(
                                                 request),
                                             response_format='html')

            dajax.add_data(
                {'target': 'div.attachment-block[object="{0!s}"]'.format(object_id), 'content': object_markup}, 'anaf.add_data')

        if update_id:
            attachments = Attachment.objects.filter(
                attached_record__id=update_id)
            template = 'core/tags/attachments_record_block'
            update_markup = render_to_string(template,
                                             {'update_id': update_id,
                                                 'attachments': attachments},
                                             context_instance=RequestContext(
                                                 request),
                                             response_format='html')
            dajax.add_data(
                {'target': 'div.attachment-record-block[object="{0!s}"]'.format(update_id), 'content': update_markup}, 'anaf.add_data')

    except Exception:
        pass

    return dajax.json()

dajaxice_functions.register(attachment)


def attachment_delete(request, attachment_id):

    try:
        a = Attachment.objects.get(pk=attachment_id)
    except Attachment.DoesNotExist:
        return

    profile = request.user.profile

    if a.attached_object:
        object_id = a.attached_object.id
        obj = Object.objects.get(pk=object_id)
    else:
        object_id = None

    update_id = None
    if a.attached_record:
        update_id = a.attached_record.id
        update = UpdateRecord.objects.get(pk=update_id)
        if not update.author == profile:
            return user_denied(request, message="Only the author of this Update can delete attachments.")

    elif not profile.has_permission(obj, mode='w'):
        return user_denied(request, message="You don't have full access to this Object")

    a.delete()

    return attachment(request, object_id, update_id)

dajaxice_functions.register(attachment_delete)


def easy_invite(request, emails=None):

    dajax = Dajax()

    try:
        emails_original = emails
        emails = emails.split(',')

        sender = request.user.profile
        default_group = sender.default_group
        domain = RequestSite(request).domain

        invited = []

        for email in emails:
            email = email.strip()
            if len(email) > 7 and re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) is not None:
                invitation = Invitation(
                    sender=request.user.profile, email=email, default_group=default_group)
                invitation.save()
                EmailInvitation(
                    invitation=invitation, sender=sender, domain=domain).send_email()
                invited.append(email)

        if invited:
            template = 'core/tags/easy_invite_success'
        else:
            template = 'core/tags/easy_invite_failure'
    except:
        template = 'core/tags/easy_invite_failure'

    invite_markup = render_to_string(template,
                                     {},
                                     context_instance=RequestContext(request),
                                     response_format='html')

    dajax.add_data({'target': "div.easy-invite[emails='{0!s}']".format(
                   (emails_original)), 'content': invite_markup}, 'anaf.add_data')
    return dajax.json()

dajaxice_functions.register(easy_invite)
