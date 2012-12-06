from mybindweb import mbforms, models
from django import forms
from django.forms import formsets
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.conf import settings
from django.db.models import Q
from datetime import datetime
from django.core.mail import EmailMessage

def offline(req):
    return render_to_response('offline.html')

# maps a user to a customer (is it safe to use pk?)
def get_customer(req):
    matches = models.Customer.objects.filter(id=req.user.id)
    if len(matches) == 0:
        raise Exception('Logged in user is not a customer.')
    else:
        return matches[0]

def index(req):
    if req.method == 'POST':
        form = mbforms.StartRegisterForm(req.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            models.Customer.start_verify(username)
            return HttpResponseRedirect(
                '/register/started/%s/' % username)
    else:
        form = mbforms.StartRegisterForm()
    
    return render_to_response('index.html', locals())

def help(req):
    return render_to_response('help.html', locals())

def contact(req):
    if req.method == 'POST':
        form = mbforms.ContactForm(req.POST)
        if form.is_valid():
            from_email = 'MyBind <%s>' % settings.EMAIL_HOST_PASSWORD
            reply_to = '%s <%s>' % (form.cleaned_data['name'],
                                    form.cleaned_data['email'])
            
            email = EmailMessage(
                'Contact form',
                form.cleaned_data['message'],
                from_email,
                [settings.CONTACT_FORM],
                headers = {'Reply-To': reply_to})

            email.send(fail_silently=False)
            
            thanks = True
    else:
        form = mbforms.ContactForm()

    return render_to_response('contact.html', locals())

def login(req):
    if req.method == 'POST':
        form = mbforms.LoginForm(req.POST, request=req)
        if form.is_valid(): # attempt auth
            form.save() # performs login
            
            customer = get_customer(req)
            customer.last_login_ip = req.META['REMOTE_ADDR']
            customer.save()
            
            return HttpResponseRedirect(req.POST['next'])
    else:
        if req.GET.has_key('next'):
            next = req.GET['next']
        else:
            next = '/account/'
        form = mbforms.LoginForm(request=req)
    
    return render_to_response('login.html', locals())

def register_started(req, email):
    if not settings.LIVE:
        test_verify = models.CustomerVerify.objects.get(customer__username=email)
    return render_to_response('register/started.html', locals())

def register_verify(req, auth_code):
    verify = models.CustomerVerify.objects.get(auth_code=auth_code)
    customer = auth.authenticate(customer=verify.customer)
    auth.login(req, verify.customer)
    return HttpResponseRedirect('/register/form/')

def about(req):
    return render_to_response('about.html', locals())

@login_required
def logout(req):
    auth.logout(req)
    return render_to_response('logout.html', locals())

@login_required
def account_index(req):
    show_admin_url = get_customer(req).is_superuser
    return render_to_response('account/index.html', locals())

def get_survey_formset_filled(survey, sub):
    
    questions = models.SurveyQuestion.objects.filter(
        survey=survey, visible=True)
    
    if len(questions) == 0:
        raise Exception(
            'No questions found for survey with ID: %i' % survey.id)

    SurveyFormset = mbforms.get_survey_formset(extra=len(questions))
    
    formset = SurveyFormset(instance=sub)
    for i in range(0, len(formset.forms)):
        ans = models.SurveyAnswer(question=questions[i])
        formset.forms[i] = mbforms.SurveyAnswerForm(
            prefix='surveyanswer_set-%i' % i, instance=ans)
    
    return formset

@login_required
def register_form(req):
    
    customer = get_customer(req)
    
    survey = models.Survey.objects.get(name='Register')
    SurveyFormset = mbforms.get_survey_formset()
    sub = models.SurveySub(
        customer=customer,
        date=datetime.now(),
        survey=survey)
    
    if req.method == 'POST':
        form = mbforms.MainRegisterForm(req.POST, instance=customer)
        sur_formset = SurveyFormset(req.POST, instance=sub)
        
        if form.is_valid() and sur_formset.is_valid():
            
            verify = models.CustomerVerify.objects.get(customer=customer)
            verify.auth_status = 1
            verify.save()
            
            form.instance.register_complete = True
            form.save()
            
            # we need to save the sub (survey submission) first, so that
            # the answers in the formset has a sub id to use
            sub.save()
            sur_formset.save()
            
            return HttpResponseRedirect('/register/done/')
    else:
        form = mbforms.MainRegisterForm(instance=get_customer(req))
        
        sur_formset = get_survey_formset_filled(survey, sub)
    
    return render_to_response('register/form.html', locals())

@login_required
def register_done(req):
    return render_to_response('register/done.html', locals())
    
@login_required
def zones_index(req):
    
    show_deleted = False
    if req.GET.has_key('show_deleted'):
        show_deleted = True
    
    deleted_q = Q(deleted=show_deleted) | Q(deleted=False)
    
    if get_customer(req).is_superuser:
        # superusers can see all zones
        zones = models.DnsZone.objects.filter(deleted_q)
    else:
        zones = models.DnsZone.objects.filter(
            Q(owner=get_customer(req)), deleted_q)
    
    return render_to_response('zones/index.html', locals())

# note: don't set delete here, this is done via the sync service
@login_required
def zones_delete(req, zone_id):
    if get_customer(req).is_superuser:
        zone = models.DnsZone.objects.get(pk=zone_id)
    else:
        zone = models.DnsZone.objects.get(pk=zone_id, owner=get_customer(req))
    
    # user may want to abort delete sync or undo a delete
    if req.GET.has_key('undo'):
        if zone.sync_cmd == 'DP':
            zone.set_ok()
        else:
            zone.set_sync('CP')
        
    else:
        if zone.deleted:
            raise Exception('Zone is already deleted.')
            
        if zone.sync_cmd == 'CP':
            # it's ok to set delete here, since it hasn't yet been created
            zone.deleted = True
            zone.sync_state = 'OK'
        else:
            # only set to delete pending if already created
            zone.set_sync('DP')
    
    zone.save()
    
    if req.META.has_key('HTTP_REFERER'):
        return HttpResponseRedirect(req.META['HTTP_REFERER'])
    else:
        return HttpResponseRedirect('/zones/')

@login_required
def zones_new(req):
    zone = models.DnsZone(owner=get_customer(req))
    zone.set_sync('CP')
    return zones_modify(req, zone)

@login_required
def zones_edit(req, zone_id):
    if req.method == 'GET':
        # on initial view, only show as many forms as there is records
        DnsRecordFormset = mbforms.get_dnszone_formset(extra=0)
    else:
        DnsRecordFormset = mbforms.get_dnszone_formset()

    if get_customer(req).is_superuser:
        zone = models.DnsZone.objects.get(pk=zone_id)
    else:
        zone = models.DnsZone.objects.get(pk=zone_id, owner=get_customer(req))
    
    if not zone.can_edit():
        raise Exception('Cannot edit when deleted or delete pending.')
    
    # change to "update pending" only if last sync was ok
    zone.set_sync('UP')
    
    return zones_modify(req, zone, DnsRecordFormset)

@login_required
def zones_modify(req, zone, DnsRecordFormset=mbforms.get_dnszone_formset()):
    if req.method == 'POST':
        zone_form = mbforms.DnsZoneForm(req.POST, instance=zone)
        rec_formset = DnsRecordFormset(req.POST, instance=zone)
        
        if zone_form.is_valid() and rec_formset.is_valid():
            zone_form.save()
            rec_formset.save()
            
            return HttpResponseRedirect('/zones/')
    else:
        zone_form = mbforms.DnsZoneForm(instance=zone)
        rec_formset = DnsRecordFormset(instance=zone)
    
    return render_to_response('zones/edit.html', locals())
