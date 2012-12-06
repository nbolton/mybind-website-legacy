from django import forms
from django.contrib import auth
from mybindweb import models
from django.utils.safestring import mark_safe
import hashlib

class PasswordField(forms.CharField):
    widget=forms.PasswordInput
    
    def __init__(self, form_values=None, repeat_check=None, *args, **kwargs):
        super(PasswordField, self).__init__(*args, **kwargs)
        self.repeat_check = repeat_check
        self.form_values = form_values
    
    def clean(self, value):
        super(PasswordField, self).clean(value)
        
        if self.repeat_check:
            if value != self.form_values[self.repeat_check]:
                raise forms.ValidationError('The two passwords do not match.')
        
        return value

class LoginForm(forms.Form):
    username = forms.EmailField(label='Email')
    password = PasswordField()
    
    def __init__(self, data=None, request=None, *args, **kwargs):
        if not request:
            raise Exception('Missing argument: request')
        self.request = request
        super(LoginForm, self).__init__(data, *args, **kwargs)
    
    def full_clean(self):
        super(LoginForm, self).full_clean()
        
        # if valid so far, try to auth
        if self.is_valid():
            try:
                self.try_auth()
            except forms.ValidationError, e:
                self._errors['password'] = e.messages
    
    def try_auth(self):
        self.user = auth.authenticate(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password']
        )
        if not self.user:
            raise forms.ValidationError('Invalid email address or password.')
    
    def save(self):
        auth.login(self.request, self.user)
    
class StartRegisterForm(forms.Form):
    username = forms.EmailField(label='Email')

class MainRegisterForm(forms.ModelForm):
    values = {}
    username = forms.EmailField(label='Email')
    password = PasswordField(label='Type password')
    password_repeat = PasswordField(
        label='Repeat password', form_values=values, repeat_check='password')
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    
    def save(self):
        self.instance.set_password(self.cleaned_data['password'])
        super(MainRegisterForm, self).save()
    
    def full_clean(self):
        # copy field values to our own dictionary, so we can easily compare
        # values between fields (such as repeated password)
        for name, field in self.fields.items():
            value = field.widget.value_from_datadict(
                self.data, self.files, self.add_prefix(name))
            self.values[name] = value
        
        # call super last, as this deletes form values
        super(MainRegisterForm, self).full_clean()
    
    class Meta:
        model = models.Customer
        fields = ('username', 'first_name', 'last_name')
        
class DnsZoneForm(forms.ModelForm):
    def __init__(self, data=None, disable_validation=False, *args, **kwargs):
        self.disable_validation = disable_validation
        super(DnsZoneForm, self).__init__(data, *args, **kwargs)
    
    def full_clean(self):
        if not self.disable_validation:
            super(DnsZoneForm, self).full_clean()
    
    class Meta:
        model = models.DnsZone
        exclude = ('raw', 'owner', 'serial', 'sync_cmd', 'sync_state',
                   'sync_msg', 'renamed', 'deleted')

class DnsRecordForm(forms.ModelForm):
    RECORD_TYPES = (
        ('A', 'A (Primary)'),
        ('CNAME', 'CNAME (Canonical name)'),
        ('MX', 'MX (Mail exchange)'),
        ('TXT', 'TXT (Text)'),
        ('PTR', 'PTR (Pointer record)'),
    )
    type = forms.ChoiceField(choices=RECORD_TYPES)
    ttl = forms.CharField(required=False, widget=forms.TextInput(attrs={'size' : 1}))
    aux = forms.CharField(required=False, widget=forms.TextInput(attrs={'size' : 1}))
    
    class Meta:
        model = models.DnsRecord
        exclude = ('zone')

def get_dnszone_formset(extra=1, **kwargs):
    return forms.models.inlineformset_factory(
        models.DnsZone,
        models.DnsRecord,
        DnsRecordForm,
        #forms.models.BaseInlineFormSet, # dont think we need this
        extra=extra,
        **kwargs)

def get_survey_formset(extra=0, **kwargs):
    return forms.models.inlineformset_factory(
        models.SurveySub,
        models.SurveyAnswer,
        SurveyAnswerForm,
        extra=extra,
        **kwargs)

class SurveyQuestionWidget(forms.HiddenInput):
    def render(self, name, value, attrs=None):
        output = super(SurveyQuestionWidget, self).render(name, value, attrs)
        if value:
            # output the input element so the question is set on submit, and
            # add to this the text for the actual question
            text = models.SurveyQuestion.objects.get(pk=value).question
            return mark_safe(output + text)
        else:
            return output

class SurveyAnswerForm(forms.ModelForm):
    sub = forms.ModelChoiceField(
        queryset=models.SurveySub.objects, widget=forms.HiddenInput)
    question = forms.ModelChoiceField(
        queryset=models.SurveyQuestion.objects, widget=SurveyQuestionWidget)
    
    class Meta:
        model = models.SurveyAnswer

class ContactForm(forms.Form):
    values = {}
    name = forms.CharField(label='Your name')
    email = forms.EmailField(label='Your email')
    message = forms.CharField(label='Message', widget=forms.Textarea)
