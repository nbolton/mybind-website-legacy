from mybindweb import models
from django.contrib import admin, auth
from django import forms

class UserForm(forms.ModelForm):
    username = forms.EmailField(
        max_length=64,
        help_text="Email address as username.",
        label="Email")
    
    class Meta:
        model = auth.models.User
        exclude = ('email',)

class UserAdmin(admin.ModelAdmin):
    form = UserForm
    list_display = ('username', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff',)
    search_fields = ('username',)

class SurveySubInline(admin.TabularInline):
    model = models.SurveySub
    extra = 0
    template = 'admin/survey_sub_inline.html'

class SurveyQuestionInline(admin.TabularInline):
    model = models.SurveyQuestion

class SurveyAnswerInline(admin.TabularInline):
    model = models.SurveyAnswer
    extra = 0
    template = 'admin/survey_answer_inline.html'

class SurveyAdmin(admin.ModelAdmin):
    inlines = [SurveyQuestionInline, SurveySubInline]

class SurveySubAdmin(admin.ModelAdmin):
    inlines = [SurveyAnswerInline,]
    list_display = ('survey', 'date', 'customer')

admin.site.register(models.Customer)
admin.site.register(models.CustomerVerify)
admin.site.register(models.DnsZone)
admin.site.register(models.DnsRecord)
admin.site.register(models.Survey, SurveyAdmin)
admin.site.register(models.SurveySub, SurveySubAdmin)
admin.site.register(models.SurveyQuestion)
admin.site.register(models.SurveyAnswer)

# replace user model (username is used as email)
admin.site.unregister(auth.models.User)
admin.site.register(auth.models.User, UserAdmin)
