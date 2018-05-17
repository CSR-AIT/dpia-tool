from django.contrib import admin
from dpia.forms import *
from dpia.models import *
from reversion.admin import VersionAdmin


class ProfileInline(admin.TabularInline):
    model =UserProfile
    extra = 0

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','expertise',]

# activate users.
def activate_user(self, request, queryset):
    users_activated = queryset.update(is_active=True)
    if users_activated == 1:
        message_bit = "1 user was"
    else:
        message_bit = "%s users were" % users_activated
    self.message_user(request, "%s successfully activated." % message_bit)
activate_user.short_description  = "Activate selected users"

# deactivate users.
def deactivate_user(self, request, queryset):
    users_deactivated = queryset.update(is_active=False)
    if users_deactivated == 1:
        message_bit = "1 user was"
    else:
        message_bit = "%s users were" % users_deactivated
    self.message_user(request, "%s successfully deactivated." % message_bit)
deactivate_user.short_description  = "Deactivate selected users"

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active',)
    fieldsets = [
            (None, {'fields': ['username', 'password', 'email', 'first_name', 'last_name','is_active','is_staff', 'is_superuser', 'user_permissions']}),
    ]
    inlines = [ProfileInline]
    list_filter = ('is_active', 'date_joined', 'last_login', 'is_superuser',)
    actions = [activate_user, deactivate_user]



## Questionnaire AdminForms.
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('member', 'questionaire',)

class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0

class SourceInline(admin.TabularInline):
    model = SourceInventory
    extra = 0

class UseCaseInline(admin.TabularInline):
    model = UseCase
    extra = 0

@admin.register(Questionaire)
class QuestionaireAdmin(admin.ModelAdmin):
    list_display = ['description',]
    # inlines = [MembershipInline, SourceInline, UseCaseInline]
    search_fields = ['description']
    inlines = [MembershipInline]


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['content',]
    # fieldsets = [
    #         (None, {'fields': ['content']}),
    # ]
    inlines = [AnswerInline]

class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'questionaire', 'answer',]

class SourceInventoryAdmin(admin.ModelAdmin):
    list_display = [ 'name', 'questionaire', 'source_file',]

class ProcessInline(admin.TabularInline):
    model = Process
    extra = 0

class UseCaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain', 'description', 'business_goal', 'questionaire', ]
    inlines = [ProcessInline]


class ProcessAdmin(admin.ModelAdmin):
    list_display = ['description', 'usecase', 'information_producer', 'information_receiver', 'information_exchanged',]


class ActorAdmin(admin.ModelAdmin):
    list_display = ['usecase', 'name', 'description', 'actor_type',]


class PrimarySupportingRelAdmin(admin.ModelAdmin):
    list_display = ['primary', 'supporting',]


class PrimarySupportingRelInline(admin.TabularInline):
    model = PrimarySupportingRel
    extra = 1

class PrimaryAdmin(admin.ModelAdmin):
    list_display = ['name', 'questionaire', 'required',]
    inlines = (PrimarySupportingRelInline,)
    # filter_horizontal = ('supporting',)

class Threat_SA_RELInline(admin.TabularInline):
    model = Threat_SA_REL
    extra = 1

class SupportingAdmin(admin.ModelAdmin):
    list_display = ['description', 'supporting_type', 'questionaire',]
    inlines = (Threat_SA_RELInline,)

class ThreatAdmin(admin.ModelAdmin):
    list_display = ['name', 'description',]

class Threat_SA_RELAdmin(admin.ModelAdmin):
    list_display = ['affected_supporting_asset', 'threat', 'control', 'level_of_vulnerability', 'risk_source_capability', 'likelihood',]


# class RiskPrimaryRelInline(admin.TabularInline):
#     model = RiskPrimaryRel
#     extra = 1

class RiskAdmin(admin.ModelAdmin):
    list_display = ['consequences', 'primary_asset_affected', 'max_likelihood', 'impact', 'risk_level',]

# Privacy Targets and Privacy Threats
class PrivacyThreatControlInline(admin.TabularInline):
    model = PrivacyThreatControl
    extra = 0

class PrivacyThreatAdmin(admin.ModelAdmin):
    list_display = ['name', 'description',]

class PrivacyThreatRelAdmin(admin.ModelAdmin):
    list_display = ['id','privacy_threat', 'privacy_q_rel',]
    inlines = (PrivacyThreatControlInline,)

class PrivacyThreatRelInline(admin.TabularInline):
    model = PrivacyThreatRel
    extra = 0

class PrivacyControlAdmin(admin.ModelAdmin):
    list_display = ['name',]


class PrivacyQuestionaireRelAdmin(admin.ModelAdmin):
    list_display = ['questionaire', 'privacy_target',]
    inlines = (PrivacyThreatRelInline,)

# 2
class PrivacyQuestionaireRelInline(admin.TabularInline):
    model = PrivacyQuestionaireRel
    extra = 0

class PrivacyTargetAdmin(admin.ModelAdmin):
    list_display = ['name', 'description',]
    inlines = (PrivacyQuestionaireRelInline,)



## AUTH
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, ProfileAdmin)
## Questionnaire
# admin.site.register(Questionaire, QuestionaireAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(SourceInventory, SourceInventoryAdmin)
admin.site.register(UseCase, UseCaseAdmin)
admin.site.register(Process, ProcessAdmin)
admin.site.register(Actor, ActorAdmin)
admin.site.register(Primary, PrimaryAdmin)
admin.site.register(Supporting, SupportingAdmin)
admin.site.register(PrimarySupportingRel, PrimarySupportingRelAdmin)
admin.site.register(Threat_SA_REL, Threat_SA_RELAdmin)
admin.site.register(Threat, ThreatAdmin)
admin.site.register(Risk, RiskAdmin)
admin.site.register(PrivacyTarget, PrivacyTargetAdmin)
admin.site.register(PrivacyThreat, PrivacyThreatAdmin)
admin.site.register(PrivacyThreatRel, PrivacyThreatRelAdmin)
admin.site.register(PrivacyControl, PrivacyControlAdmin)
admin.site.register(PrivacyQuestionaireRel, PrivacyQuestionaireRelAdmin)

## 3d party apps
