from django.contrib.staticfiles import finders
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session
from django.contrib.sites.models import RequestSite
from django.utils.encoding import smart_unicode
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_control
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import resolve, reverse, Resolver404
from django.shortcuts import get_object_or_404
from conf import settings
from decorators import mylogin_required, handle_response_format, require_response_format
from forms import LoginForm, PasswordResetForm, InvitationForm, SqlSettingsForm
from models import Object, Module, ModuleSetting, Perspective, User, Attachment, Invitation, Tag, \
    UpdateRecord
from rendering import render_to_response
from jinja2 import Markup
from os.path import join
import re
import json
import urllib2
import random


@handle_response_format
@mylogin_required
def user_logout(request, response_format='html'):
    """User logout"""
    logout(request)
    return HttpResponseRedirect(reverse('user_login'))


@handle_response_format
def user_login(request, response_format='html'):
    "User login"
    if request.user.username:
        return HttpResponseRedirect(reverse('user_denied'))
    next = request.GET.get('next', '/')
    form = LoginForm(request.POST)
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user and getattr(settings, 'HARDTREE_DISABLE_EVERGREEN_USERS', False) and 'evergreen_' in user.username[:10]:
            user = None
        if form.is_valid():
            if user is not None:

                try:
                    profile = user.profile
                except:
                    profile = None

                if not profile:
                    return render_to_response('core/user_login', {
                        'error_message': 'Username or password you entered is not valid', 'form': Markup(form)},
                                              context_instance=RequestContext(request), response_format=response_format)

                if profile.disabled:
                    return render_to_response('core/user_login', {
                        'error_message': 'Your account is disabled.',
                        'form': Markup(form)},
                                              context_instance=RequestContext(request),
                                              response_format=response_format)

                if user.is_active and profile:

                    # Disable account with overdue payment
                    if settings.ANAF_SUBSCRIPTION_BLOCKED:
                        return render_to_response('core/user_login', {
                            'error_message': 'We are sorry to inform you but your account has been deactivated. Please login to your control panel to see details.',
                            'form': Markup(form)},
                                                  context_instance=RequestContext(request),
                                                  response_format=response_format)

                    login(request, user)

                    # Prevent same user from logging in at 2 different machines
                    if settings.ANAF_MULTIPLE_LOGINS_DISABLED:
                        for ses in Session.objects.all():
                            if ses != request.session:
                                try:
                                    data = ses.get_decoded()
                                    if '_auth_user_id' in data and data['_auth_user_id'] == request.user.id:
                                        ses.delete()
                                except Exception:
                                    pass

                    if 'next' in request.POST:
                        return HttpResponseRedirect(request.POST['next'])
                    else:
                        return HttpResponseRedirect(next)
                else:
                    return render_to_response('core/user_login_disabled',
                                              context_instance=RequestContext(
                                                  request),
                                              response_format=response_format)
            else:
                return render_to_response('core/user_login', {
                    'error_message': 'Username or password you entered is not valid', 'form': Markup(form)},
                                          context_instance=RequestContext(request), response_format=response_format)
        elif not form.is_valid() and user is None:
            return render_to_response('core/user_login',
                                      {'error_message': 'Username or password you entered is not valid', 'form': Markup(
                                          form)},
                                      context_instance=RequestContext(request), response_format=response_format)
        else:
            return render_to_response('core/user_login',
                                      {'error_message': 'Please re-enter the text from the image',
                                       'form': Markup(form)},
                                      context_instance=RequestContext(request), response_format=response_format)
    else:
        return render_to_response('core/user_login', {'form': Markup(form)},
                                  context_instance=RequestContext(request), response_format=response_format)


@handle_response_format
def user_denied(request, message='', response_format='html'):
    "User denied page"
    response = render_to_response('core/user_denied',
                                  {'message': message},
                                  context_instance=RequestContext(request), response_format=response_format)
    # response.status_code = 403
    return response


@mylogin_required
@handle_response_format
def user_perspective(request, response_format='html'):
    "Change user perspective"

    user = request.user.profile
    if request.POST and 'core_perspective' in request.POST:
        id = request.POST['core_perspective']
        perspective = get_object_or_404(Perspective, pk=id)
        if user.has_permission(perspective):
            user.set_perspective(perspective)

    return HttpResponseRedirect(reverse('home'))


@cache_control(private=True, must_revalidate=True, max_age=60)
def logo_image(request, gif=False, response_format='html'):
    """Return current logo image
    :param bool gif: if not gif it is png
    :param string response_format:
    """

    # FIXME: logo file loading logic sucks, maybe use x-sendfile
    try:
        conf = ModuleSetting.get_for_module('anaf.core', 'logopath')[0]
        path = getattr(settings, 'MEDIA_ROOT', './static/media') + conf.value
        if path.endswith('.gif'):
            mimetype = 'image/gif'
        else:
            mimetype = 'image/png'
    except:
        # if there isn't a custom logo we use the default
        if gif:
            extension = 'gif'
        else:
            extension = 'png'
        filename = 'logo.{}'.format(extension)
        mimetype = 'image/{}'.format(extension)
        path = finders.find(filename)

    try:
        with open(path, 'rb') as logofile:
            return HttpResponse(logofile.read(), content_type=mimetype)
    except IOError:
        raise Http404(path)


def get_active(url):
    modules = Module.objects.all()
    active = None
    for module in modules:
        try:
            import_name = module.name + "." + \
                          settings.ANAF_MODULE_IDENTIFIER
            hmodule = __import__(import_name, fromlist=[str(module.name)])
            urls = hmodule.URL_PATTERNS
            for regexp in urls:
                if re.match(regexp, url):
                    active = module
        except ImportError:
            pass
        except AttributeError:
            pass
    return active


def ajax_popup(request, popup_id='', url='/'):
    """Handles pop up forms and requests, by extracting only the required content from response content"""
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/accounts/login')
    try:
        view, args, kwargs = resolve(url)
    except Resolver404:
        raise Http404('Invalid popup URL')

    active = get_active(url)

    if active and not request.user.profile.has_permission(active):
        response = user_denied(request, "You do not have access to the {0!s} module".format(unicode(active)),
                               response_format='ajax')

    else:
        if view == ajax_popup:
            # todo: return 401 and not 404 HttpResponseBadRequest()
            raise Http404("OMG, I see myself!")

        kwargs['request'] = request
        kwargs['response_format'] = 'ajax'
        response = view(*args, **kwargs)

        # response = csrf().process_response(request, response)

    module_inner = ""
    regexp = r"<!-- module_content_inner -->(?P<module_inner>.*?)<!-- /module_content_inner -->"
    blocks = re.finditer(regexp, response.content, re.DOTALL)
    for block in blocks:
        module_inner += block.group('module_inner').strip()

    title = ""
    regexp = r"<div class=\\\"title\\\">(?P<title>.*?)</div>"
    blocks = re.finditer(regexp, response.content, re.DOTALL)
    for block in blocks:
        title += block.group('title').replace('\\n', '').strip()
    if not title:
        blocks = re.finditer(
            r"<title>(?P<title>.*?)</title>", response.content, re.DOTALL)
        for block in blocks:
            title += block.group('title').replace('\\n', '').strip()

    subtitle = ""
    regexp = r"<div class=\\\"subtitle-block\\\">(?P<subtitle>.*?)</div>"
    blocks = re.finditer(regexp, response.content, re.DOTALL)
    for block in blocks:
        subtitle += block.group('subtitle').replace('\\n', '').strip()

    context = {'content': module_inner, 'title': title, 'subtitle': subtitle, 'popup_id': popup_id, 'url': request.path}

    if settings.ANAF_RESPONSE_FORMATS['json'] in response.get('Content-Type', 'text/html'):
        new_response = render_to_response('core/ajax_popup', context,
                                          context_instance=RequestContext(request), response_format='json')
    else:
        new_response = HttpResponse(json.dumps({'popup': context}))

    new_response.mimetype = settings.ANAF_RESPONSE_FORMATS['json']
    try:
        jsonresponse = json.loads(response.content)
        if 'redirect' in jsonresponse:
            new_response.status_code = 302
    except Exception:
        new_response.status_code = response.status_code

    return new_response


def mobile_view(request, url='/'):
    "Returns the same page in mobile view"

    if not url:
        url = '/'

    view, args, kwargs = resolve(url)

    if view == mobile_view:
        raise Http404("OMG, I see myself!")

    kwargs['request'] = request
    kwargs['response_format'] = 'html'
    response = view(*args, **kwargs)

    # response = csrf().process_response(request, response)

    if response.status_code == 302 and not response['Location'][:2] == '/m':
        response['Location'] = '/m' + response['Location']

    return response


def iframe_close(request, response_format='html'):
    "For third-party resources, when returned back to Anaf, close iframe"

    return render_to_response('core/iframe_close', {},
                              context_instance=RequestContext(request),
                              response_format=response_format)


@handle_response_format
def database_setup(request, response_format='html'):
    if not User.objects.all().count():
        if request.POST:
            sql_form = SqlSettingsForm(data=request.POST)
            if sql_form.is_valid():
                sql_form.create_database()
                if sql_form.is_valid():
                    return HttpResponseRedirect('/')
        else:
            sql_form = SqlSettingsForm()
        return render_to_response('core/database_setup', {'sql_form': sql_form},
                                  context_instance=RequestContext(request), response_format=response_format)
    return HttpResponseRedirect('/')


@mylogin_required
def help_page(request, url='/', response_format='html'):
    "Returns a Help page from Evergreen"

    source = settings.ANAF_HELP_SOURCE

    if not url:
        url = '/'

    body = ''
    try:
        body = urllib2.urlopen(
            source + url + '?domain=' + RequestSite(request).domain).read()
    except:
        pass

    regexp = r"<!-- module_content_inner -->(?P<module_inner>.*?)<!-- /module_content_inner -->"
    blocks = re.finditer(regexp, body, re.DOTALL)
    for block in blocks:
        body = smart_unicode(block.group('module_inner').strip())

    return render_to_response('core/help_page', {'body': body},
                              context_instance=RequestContext(request),
                              response_format=response_format)


#
# AJAX lookups
#
@mylogin_required
def ajax_object_lookup(request, response_format='html'):
    "Returns a list of matching objects"

    objects = []
    if request.GET and 'term' in request.GET:
        objects = Object.filter_permitted(request.user.profile,
            Object.objects.filter(
                object_name__icontains=request.GET['term']),
            mode='x')[:10]

    return render_to_response('core/ajax_object_lookup',
                              {'objects': objects},
                              context_instance=RequestContext(request),
                              response_format=response_format)


@require_response_format(['json'])
@mylogin_required
def ajax_tag_lookup(request, response_format='json'):
    """Returns a list of matching tags"""

    tags = []
    if request.GET and 'term' in request.GET:
        tags = Tag.objects.filter(name__icontains=request.GET['term'])

    return render_to_response('core/ajax_tag_lookup',
                              {'tags': tags},
                              context_instance=RequestContext(request),
                              response_format=response_format)


#
# Widgets
#


@mylogin_required
def widget_welcome(request, response_format='html'):
    "Quick start widget, which users see when they first log in"

    trial = False
    if settings.ANAF_SUBSCRIPTION_USER_LIMIT == 3:
        trial = True

    customization = settings.ANAF_SUBSCRIPTION_CUSTOMIZATION

    return render_to_response('core/widgets/welcome', {'trial': trial, 'customization': customization},
                              context_instance=RequestContext(request), response_format=response_format)


#
# Passwords
#
@csrf_protect
def password_reset(request, response_format='html'):
    "Password_reset sends the email with the new password"

    if request.POST:
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('password_reset_done'))
    else:
        form = PasswordResetForm()

    return render_to_response('core/password_reset_form',
                              {'form': form},
                              context_instance=RequestContext(request),
                              response_format=response_format)


def password_reset_done(request, response_format='html'):
    "Shows success message"

    return render_to_response('core/password_reset_done',
                              context_instance=RequestContext(request),
                              response_format=response_format)


def invitation_retrieve(request, response_format='html'):
    "Retrieve invitation and create account"

    if request.user.username:
        return HttpResponseRedirect('/')

    email = request.REQUEST.get('email')
    key = request.REQUEST.get('key')
    if email and key:
        try:
            invitation = Invitation.objects.get(email=email, key=key)
        except Invitation.DoesNotExist:
            raise Http404
    else:
        raise Http404

    if request.POST:
        form = InvitationForm(invitation, request.POST)
        if form.is_valid():
            profile = form.save()
            username = profile.user.username
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                invitation.delete()
                login(request, user)
                return HttpResponseRedirect('/')
    else:
        form = InvitationForm(invitation)

    return render_to_response('core/invitation_retrieve',
                              {'invitation': invitation,
                               'form': form},
                              context_instance=RequestContext(request),
                              response_format=response_format)


def save_upload(uploaded, filename, raw_data):
    '''
    raw_data: if True, uploaded is an HttpRequest object with the file being
              the raw post data
              if False, uploaded has been submitted via the basic form
              submission and is a regular Django UploadedFile in request.FILES
    '''
    try:
        from io import FileIO, BufferedWriter

        with BufferedWriter(FileIO(filename, "wb")) as dest:
            # if the "advanced" upload, read directly from the HTTP request
            # with the Django 1.3 functionality
            if raw_data:
                if isinstance(uploaded, basestring):
                    dest.write(uploaded)
                else:
                    foo = uploaded.read(1024)
                    while foo:
                        dest.write(foo)
                        foo = uploaded.read(1024)
            # if not raw, it was a form upload so read in the normal Django
            # chunks fashion
            else:
                for c in uploaded.chunks():
                    dest.write(c)
                    # got through saving the upload, report success
            return True
    except IOError:
        # could not open the file most likely
        pass
    return False


@require_POST
@mylogin_required
def ajax_upload(request, object_id=None, record=None):
    try:
        object = None
        if request.is_ajax():
            # the file is stored raw in the request
            upload = request
            is_raw = True
            # AJAX Upload will pass the filename in the querystring if it
            # is the "advanced" ajax upload
            try:
                filename = request.GET['qqfile']
                content_type = "application/octet-stream"
            except KeyError:
                return HttpResponseBadRequest("AJAX request not valid")
        # not an ajax upload, so it was the "basic" iframe version with
        # submission via form
        else:
            is_raw = False
            if len(request.FILES) == 1:
                # FILES is a dictionary in Django but Ajax Upload gives the uploaded file an
                # ID based on a random number, so it cannot be guessed here in the code.
                # Rather than editing Ajax Upload to pass the ID in the querystring,
                # observer that each upload is a separate request,
                # so FILES should only have one entry.
                # Thus, we can just grab the first (and only) value in the
                # dict.
                upload = request.FILES.values()[0]
                content_type = upload.content_type
            else:
                raise Http404("Bad Upload")
            filename = upload.name

        random.seed()
        filehash = str(random.getrandbits(128))

        savefile = join(
            getattr(settings, 'MEDIA_ROOT'), 'attachments', filehash)

        # save the file
        success = save_upload(upload, savefile, is_raw)

        attachment = Attachment(filename=filename,
                                content_type=content_type,
                                uploaded_by=request.user.profile,
                                attached_file=filehash)

        if record:
            attachment.attached_record = record
            about = record.about.all()
            if about.count():
                attachment.attached_object = about[0]
                object = attachment.attached_object
        else:
            object = Object.objects.get(id=object_id)
            attachment.attached_object = object
            # TODO: return 404 on object.doesnotexist, also create test

        attachment.save()

        if object:
            object.set_last_updated()

        # TODO: smart markup and return as string, and object id, different
        # classnames,id or attribute for update records and objects

        if success:
            ret_json = {'success': success,
                        'object_id': object.id if object else None,
                        'update_id': record.id if record else None}

        else:
            ret_json = {'success': False,
                        'object_id': None,
                        'update_id': None}

        return HttpResponse(json.dumps(ret_json))
    except:
        pass


@mylogin_required
def ajax_upload_record(request, record_id):
    record = get_object_or_404(UpdateRecord, id=record_id)
    return ajax_upload(request, None, record)


@mylogin_required
def attachment_download(request, attachment_id):
    try:
        attachment = Attachment.objects.get(pk=attachment_id)
    except Attachment.DoesNotExist:
        raise Http404()

    filepath = join(
        getattr(settings, 'MEDIA_ROOT'), 'attachments', attachment.attached_file.name)
    try:
        data = open(filepath).read()
    except IOError:
        raise Http404()

    response = HttpResponse(data, content_type=attachment.mimetype)
    response[
        'Content-Disposition'] = 'filename="{0!s}"'.format(smart_unicode(attachment.filename))
    return response
