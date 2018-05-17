from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm, PasswordChangeForm, SetPasswordForm
from django.forms import modelformset_factory, inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.safestring import mark_safe
from django import forms
from dpia.models import *

## AUTH
# user registration form.
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password_confirm = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['password_confirm'].label = "Password confirmation"
        self.fields['email'].required = True
        # for field_name, field in self.fields.items():
        #     field.widget.attrs['class'] = 'form-control'

    ## access the clean method of password.
    MIN_LENGTH = 6
    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        email = self.cleaned_data.get('email')

        # check if username has '@'
        if username and '@' in username:
            self.add_error('username', "@ symbol is not allowed in the username.")
        # check if email is unique.
        emails = User.objects.filter(email=email).exists()
        if email and emails:
            self.add_error('email', u"Email already exists in the database.")

        # confirm password.
        if password and password_confirm:
            if password != password_confirm:
                self.add_error('password', "Passwords don't match.")
                self.add_error('password_confirm', "Passwords don't match.")

            # at least MIN_LENGTH long.
            if len(password) < self.MIN_LENGTH:
                self.add_error('password', "This password is too short. It must contain at least %d characters." % self.MIN_LENGTH)

            # entirely numeric.
            if password.isdigit():
                self.add_error('password', "This password is entirely numeric.")

            # at least one letter and one non-letter symbol.
            first_isalpha = password[0].isalpha()
            if all(c.isalpha() == first_isalpha for c in password):
                self.add_error('password', "The password must contain at least 1 letter and at least 1 digit or" \
                                            " punctuation character.")

# user update form.
class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    username = forms.CharField(required=True)
    email = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', ]

## profile form.
class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['expertise',]


## PASSWORD RESET
# Customize password reset send email form.
class CheckResetEmailForm(PasswordResetForm):
    def clean(self):
        cleaned_data = super(CheckResetEmailForm, self).clean()
        email = self.cleaned_data.get('email')
        email_exists = User.objects.filter(email=email).exists()
        if not email_exists:
            self.add_error('email', "The email you entered is not a DPIA email")
        return cleaned_data

## customize password reset password form.
class ResetPasswordChangeForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(ResetPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = None

## customize profile password change form.
class CheckPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(CheckPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = None


# //////// #

##### Qs
## Questionaire & Membership
class QuestionaireForm(forms.ModelForm):
    class Meta:
        model = Questionaire
        fields = ['description', 'aim_of_dpia',]
        widgets = {
            'description': forms.TextInput(attrs={ 'required': 'true' }),
        }



## to edit memberships
class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['responsibility_in_dpia',]



## Q-STEPS
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['content',]


### Show the Boolean radio select fields horizontally
import django
django_version = django.get_version()
from distutils.version import StrictVersion

if StrictVersion(django_version) >= '1.11':
    class HorizontalRadioSelect(forms.RadioSelect):
        template_name = 'pre-assessment/horizontal_select.html'
else:
    class HorizontalRadioRenderer(forms.RadioSelect.renderer):
      def render(self):
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))



class AnswerForm(forms.ModelForm):
    BOOL_CHOICES = (
        (True, 'Yes'),
        (False, 'No'))

    class Meta:
        model = Answer
        fields = ['answer',]
        if StrictVersion(django_version) >= '1.11':
            widgets = {
                'answer': HorizontalRadioSelect()
            }
        else:
            widgets = {
                'answer': forms.RadioSelect(renderer=HorizontalRadioRenderer)
            }


class SourceInventoryForm(forms.ModelForm):
    class Meta:
        model = SourceInventory
        fields = ['name', 'description', 'source_type', 'purpose', 'source_file']
        widgets = {
            'name': forms.TextInput(attrs={ 'required': 'true' }),
            'description': forms.TextInput(attrs={ 'required': 'true' }),
            'source_type': forms.TextInput(attrs={ 'required': 'true' }),
            'purpose': forms.TextInput(attrs={ 'required': 'true' }),
            # 'source_file': forms.widgets.FileInput()
        }


class UseCaseForm(forms.ModelForm):
    class Meta:
        model = UseCase
        fields = ['name', 'domain', 'description', 'business_goal',]
        widgets = {
            'name': forms.TextInput(attrs={ 'required': 'true' }),
            'domain': forms.TextInput(attrs={ 'required': 'true' }),
            'description': forms.TextInput(attrs={ 'required': 'true' }),
            'description': forms.Textarea(attrs={'rows':5, 'cols':19}),
            'business_goal': forms.TextInput(attrs={ 'required': 'true' }),
        }



class ProcessForm(forms.ModelForm):
    class Meta:
        model = Process
        fields = ['description', 'information_producer', 'information_receiver', 'information_exchanged',]

    def __init__(self, *args, **kwargs):
        super(ProcessForm, self).__init__(*args, **kwargs)
        self.fields['description'].required = True
        self.fields['information_producer'].required = True
        self.fields['information_receiver'].required = True
        self.fields['information_exchanged'].required = True
        self.empty_permitted = False
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['required'] = True


class ActorForm(forms.ModelForm):
    class Meta:
        model = Actor
        fields = ['name', 'description', 'actor_type',]

    def __init__(self, *args, **kwargs):
        super(ActorForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['description'].required = True
        self.fields['actor_type'].required = True
        self.empty_permitted = False
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['required'] = True

from django.forms import ModelForm
from django.core.exceptions import NON_FIELD_ERRORS


## SGAM IMPORT FORM ##
class SgamForm(forms.ModelForm):

    class Meta:
        model = SgamXml
        fields = ['xml_file',]

    def __init__(self, *args, **kwargs):
        super(SgamForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
## /SGAM FORm END ##


class PrimaryForm(forms.ModelForm):
    class Meta:
        model = Primary
        fields = ['name', 'reading_frequency', 'retention_time', 'data_subjects', 'level_of_identification',]
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "%(model_name)s's %(field_labels)s are not unique.",
            }
        }

    #
    # def clean(self):
    #     cleaned_data = super(PrimaryForm, self).clean()
    #     primary_name = cleaned_data.get("name")
    #     primary = Primary.objects.all().filter(name=primary_name, questionaire=self.instance.questionaire)
    #     if primary.exists():
    #         msg = "Primary Asset with this Name already exists for this Questionaire"
    #         self.add_error('name', msg)

    ## Override Form
    def __init__(self, *args, **kwargs):
        super(PrimaryForm, self).__init__(*args, **kwargs)
        # self.fields['required'].empty_label = None
        # self.fields['required'].required = True
        self.fields['level_of_identification'].help_text = 'Instructions'
        # self.fields['required'].help_text = 'If false, the primary asset will not be considered in the following steps.'
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['required'] = True


class PrimaryForm2(forms.ModelForm):
    class Meta:
        model = Primary
        fields = ['reading_frequency', 'retention_time', 'level_of_identification',]

    ## Override Form
    def __init__(self, *args, **kwargs):
        super(PrimaryForm2, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['required'] = True

class SupportingForm(forms.ModelForm):
    class Meta:
        model = Supporting
        fields = ['description','supporting_type',]

    def __init__(self, *args, **kwargs):
        super(SupportingForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['required'] = True

class PrimarySupportingRelForm(forms.ModelForm):
    class Meta:
        model = PrimarySupportingRel
        exclude = ['primary', 'supporting',]


class ThreatForm(forms.ModelForm):
    class Meta:
        model = Threat
        fields = ['name', 'type_of_jeopardy', 'description', 'motivation',]
        widgets = {
            'description': forms.Textarea(attrs={'rows':2, 'cols':19}),
            'motivation': forms.Textarea(attrs={'rows':2, 'cols':19}),
        }

    def __init__(self, *args, **kwargs):
        super(ThreatForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['required'] = True


# Threat Assessment
# LEVEL_CHOICES = (
#     (0, '---------'),
#     (1, "Negligible"),
#     (2, "Limited"),
#     (3, "Significant"),
#     (4, "Maximum"),
#     )
#
# class ThreatAssessmentForm(forms.Form):
#     level_of_vulnerability = forms.ChoiceField(
#         label="",
#         required=True,
#         choices=LEVEL_CHOICES,
#         # widget=forms.Select(attrs={'name': 'level_of_vulnerability', 'class': '', 'onchange': 'this.form.submit();'}),
#     )
#
#     # def __init__(self, *args, **kwargs):
#     #     super(ThreatAssessmentForm, self).__init__(*args, **kwargs)
#     #     self.fields['level_of_vulnerability'].choices.insert(0, ('','---------' ) )


class Threat_SA_REL_Form(forms.ModelForm):
    class Meta:
        model = Threat_SA_REL
        fields = ['level_of_vulnerability', 'risk_source_capability',]
        # widgets = {
        #     'level_of_vulnerability': forms.Select(attrs={'onchange': 'this.form.submit();'}),
        #     'risk_source_capability': forms.Select(attrs={'onchange': 'this.form.submit();'})
        # }

    def __init__(self, *args, **kwargs):
        super(Threat_SA_REL_Form, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['required'] = True


class Threat_SA_REL_Form2(forms.ModelForm):
    class Meta:
        model = Threat_SA_REL
        fields = ['control',]
        widgets = {
            'control': forms.Textarea(attrs={'rows':4, 'cols':19}),
        }

    def __init__(self, *args, **kwargs):
        super(Threat_SA_REL_Form2, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            self.fields['control'].required = True
            for field_name, field in self.fields.items():
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['required'] = True


class RiskForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = ['prejudicial_effects', 'risk_owner', 'consequences',]
        widgets = {
            'consequences': forms.Textarea(attrs={'rows':4, 'cols':19}),
        }

    ## Make ForeignKey Fields Readonly
    def __init__(self, *args, **kwargs):
        super(RiskForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            self.fields['prejudicial_effects'].required = True
            self.fields['risk_owner'].required = True
            self.fields['consequences'].required = True
            for field_name, field in self.fields.items():
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['required'] = True



class RiskForm2(forms.ModelForm):
    class Meta:
        model = Risk
        fields = ['risk_treatment', 'residual_risk', ]
        widgets = {
            'risk_treatment': forms.Textarea(attrs={'rows':4, 'cols':19}),
            'residual_risk': forms.Textarea(attrs={'rows':4, 'cols':19}),
            # 'control': forms.Textarea(attrs={'rows':4, 'cols':19}),
        }

    def __init__(self, *args, **kwargs):
        super(RiskForm2, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            # self.fields['risk_treatment'].required = True
            # self.fields['residual_risk'].required = True
            for field_name, field in self.fields.items():
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['required'] = True

#  Privacy Targets, Threats, Controls
class PrivacyControlForm(forms.ModelForm):
    class Meta:
        model = PrivacyControl
        fields = ['name',]

class PrivacyTargetForm(forms.ModelForm):
    class Meta:
        model = PrivacyTarget
        fields = ['name','description',]


class PrivacyThreatForm(forms.ModelForm):
    class Meta:
        model = PrivacyThreat
        fields = ['privacy_controls',]
        widgets = {
            'privacy_controls': forms.CheckboxSelectMultiple(),
        }


class PrivacyThreatRelForm(forms.ModelForm):
    class Meta:
        model = PrivacyThreatRel
        fields = ['affected_primary_assets',]
        widgets = {
            'affected_primary_assets': forms.CheckboxSelectMultiple(),
        }



# class ContactForm(forms.Form):
#     full_name = forms.CharField()
#     email = forms.EmailField()
#     message = forms.CharField(widget=forms.Textarea)


### Export format
class ExportFormatForm(forms.Form):
    FORMAT_CHOICES = (
        (1, ("xls")),
        (2, ("json")),
        (3, ("csv")),
    )
    file_format = forms.ChoiceField(choices=(FORMAT_CHOICES), label="Format", widget=forms.Select(), required=True)
