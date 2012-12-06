from django.db import models
from django.contrib.auth.models import User as DjangoUser
from django.conf import settings
from django.core import mail
import datetime
import random
import hashlib
from django.utils.safestring import mark_safe

# username should be upto 320 chars (max email), but unique fields are max 255
DjangoUser._meta.get_field_by_name('username')[0].max_length=255

class Customer(DjangoUser):
    last_login_ip = models.IPAddressField(blank=True, null=True)
    
    register_date = models.DateTimeField(auto_now=True)
    register_complete = models.BooleanField()
    
    @staticmethod
    def start_verify(username):
        customer, customer_created = Customer.objects.get_or_create(username=username)
        
        hash = hashlib.sha1(str(random.random())).hexdigest()
        
        verify = CustomerVerify()
        verify.customer = customer
        verify.auth_code = hash
        verify.auth_status = 0
        verify.save()
        
        from_name = settings.ACTIVATE_FROM_NAME
        from_email = settings.ACTIVATE_FROM_EMAIL
        to_email = [username] # username is email address
        
        verify_url = "http://www.mybind.com/register/verify/%s/" % hash
        
        msg_html = ('<p>Hello,</p>'
                    '<p>Please <a href="%s">activate your account</a>.</p>'
                    '<p>Thanks,<br/>MyBind</p>') % verify_url
        
        msg = mail.EmailMessage(
            'Activate account', msg_html,
            '%s <%s>' % (from_name, from_email), to_email)
        msg.content_subtype = "html"
        msg.send()
        
        return customer
    
    def __unicode__(self):
        if self.first_name and self.last_name:
            return '%s %s (%s)' % (self.first_name, self.last_name, self.username)
        elif self.first_name:
            return '%s (%s)' % (self.first_name, self.username)
        elif self.last_name:
            return '%s (%s)' % (self.last_name, self.username)
        else:
            return self.username

class Survey(models.Model):
    name = models.CharField(max_length=50)
    created = models.DateTimeField()
    
    def __unicode__(self):
        return self.name
    
class SurveyQuestion(models.Model):
    survey = models.ForeignKey(Survey)
    question = models.CharField(max_length=200)
    visible = models.BooleanField()
    
    def __unicode__(self):
        return self.question

class SurveySub(models.Model): # survey submission
    survey = models.ForeignKey(Survey)
    customer = models.ForeignKey(Customer)
    date = models.DateTimeField()
    
    def __unicode__(self):
        return '%s - %s' % (self.date.ctime(), self.customer)

class SurveyAnswer(models.Model):
    sub = models.ForeignKey(SurveySub)
    question = models.ForeignKey(SurveyQuestion)
    answer = models.CharField(max_length=200)
    
    def __unicode__(self):
        return mark_safe('%s <b>%s</b>' % (self.question, self.answer))

class CustomerVerify(models.Model):
    STATUS_TYPES = (
        (0, 'Sent'),
        (1, 'Verified')
    )
    customer = models.ForeignKey(Customer)
    auth_code = models.CharField(max_length=50)
    auth_status = models.IntegerField(choices=STATUS_TYPES)
    
    def __unicode__(self):
        return '%s (%s)' % (self.auth_code, self.get_auth_status_display())

class DnsZone(models.Model):
    SYNC_CMD_CHOICES = (
        ('OK', 'Nothing to do'),
        ('CP', 'Create pending'),
        ('UP', 'Update pending'),
        ('DP', 'Delete pending')
    )
    SYNC_STATE_CHOICES = (
        ('OK', 'Up to date'),
        ('SP', 'Sync pending'),
        ('SA', 'Sync active'),
        ('SE', 'Sync error')
    )
    
    owner = models.ForeignKey(Customer)
    name = models.CharField(max_length=200, verbose_name='zone name', unique=True)
    default_ttl = models.CharField(
        max_length=10, blank=True, null=True,
        verbose_name='Default TTL', default='1h')
    serial = models.CharField(max_length=12) # yyyymmddrr (and 2 extra for overflow)
    sync_cmd = models.CharField(max_length=2, choices=SYNC_CMD_CHOICES)
    sync_state = models.CharField(max_length=2, choices=SYNC_STATE_CHOICES)
    sync_msg = models.CharField(max_length=200, blank=True, null=True)
    renamed = models.BooleanField()
    deleted = models.BooleanField()
    
    def __init__(self, *args, **kwargs):
        super(DnsZone, self).__init__(*args, **kwargs)
        self.original_name = self.name
    
    def sync_status_msg(self):
        if self.sync_state == 'SP': # sync pending?
            return self.get_sync_cmd_display()
        else:
            return self.get_sync_state_display()
    
    def increment_serial(self):
        
        # default revision is 0
        revision = 0
        
        # default date is today
        date = datetime.date.today()
            
        if self.serial:
            
            # get existing date
            date = datetime.datetime.strptime(self.serial[0:8], '%Y%m%d')
            
            if date.date().today() == datetime.date.today():
                # increment existing revision if same date
                revision = int(self.serial[8:]) + 1
        
        self.serial = date.strftime('%Y%m%d') + str(revision).zfill(2)
    
    def record_count(self):
        return DnsRecord.objects.filter(zone=self).count()
    
    def can_edit(self):
        return not self.deleted and self.sync_cmd != 'DP'
    
    def set_sync(self, cmd, state='SP'):
        self.sync_cmd = cmd
        self.sync_state = state
    
    def set_ok(self):
        self.sync_cmd = 'OK'
        self.sync_state = 'OK'
    
    def save(self):
        if self.sync_state == 'SA': # sync active?
            raise Exception('Cannot save; sync in progress.')
        
        # its important for the sync process to know if zone was renamed
        self.renamed = self.name != self.original_name
        
        self.increment_serial()
        super(DnsZone, self).save()
    
    def __unicode__(self):
        return self.name

class DnsRecord(models.Model):
    # keep it simple for now
    RECORD_TYPES = (
        ('MX', 'MX (Mail exchange)'),
        ('A', 'A (Primary)'),
        ('CNAME', 'CNAME (Canonical name)'),
        ('TXT', 'TXT (Text)'),
    )
    zone = models.ForeignKey(DnsZone)
    name = models.CharField(max_length=250) # isc bind max = ?
    type = models.CharField(max_length=5, choices=RECORD_TYPES)
    ttl = models.CharField(max_length=10, blank=True, null=True, verbose_name='TTL')
    aux = models.CharField(max_length=50, blank=True, null=True) # mx priority, etc
    data = models.CharField(max_length=1500) # isc bind reccomended max = 450
    
    def __unicode__(self):
        return '%s - %s' % (self.type, self.name)
