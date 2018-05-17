#!/usr/bin/env python
# coding: utf8

from django.db import models
from django.db.models import signals, Sum, Q
from django.db.models.signals import pre_save, post_save
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Permission
from django.template import RequestContext
from django.dispatch import receiver
from django.shortcuts import redirect, render, get_object_or_404
# 3rd party apps
import reversion
from reversion import revisions as reversion
from reversion.models import Revision
# python modules
import os

class VersionOwner(models.Model):
    # There must be a relationship with Revision called `revision`.
    revision = models.OneToOneField(Revision)
    owner_id = models.IntegerField(null=True)


# Adds Profile Model, which inherits from the base User Model of Django
class UserProfile(models.Model):
    """ The Profile class defines the main storage point for User Profiles.
        Each Profile includes all the fields of the django base user:
        - **first_name** - stores the first name of the user.
        - **last_name** - stores the last name of the user.
        - **username** - stores the username of the user.
        - **email** - stores the email of the user.
        - **password** - stores the password of the user.
        - **is_active** - controls if the user is activated or not.
        ... and an additional field:
        - **expertise** - stores the expertise of the User.
    """
    # one to one relationship to the user base model.
    user = models.OneToOneField(User, blank=False, on_delete=models.CASCADE, related_name="user_profile")
    # attribute of the profile
    expertise = models.CharField(max_length=100, blank=False)
    # override the __unicode__() method to return out the full name of the user.
    def __unicode__(self):
        return '%s' %(self.user.get_full_name())


## Models of the Questionnaire
class Questionaire(models.Model):
    """ The Questionaire class defines the main storage point for Questionnaires.
        Each Questionaire has these fields:
        - **description** - stores the description of the questionnaire.
        - **aim_of_dpia** - stores the aim of the DPIA Questionnaire.
        - **members** - stores the username of the user.
        - **step_source** - stores an int value (10) when a source is added to the questionnaire. When there are no sources, the value is 0. The same principle applies to all the other step fields.
    """

    description = models.CharField(max_length=255, blank=False)
    aim_of_dpia = models.CharField(max_length=255, blank=True)
    members = models.ManyToManyField(User, through='Membership', help_text="ManytoOne-Relationship to Members")

    # check if every model related to the questionnaire model has instances
    def has_sources(self):
        return SourceInventory.objects.select_related('questionaire').filter(questionaire=self.id).exists()
    def has_primary_assets(self):
        return Primary.objects.filter(questionaire=self.id, reading_frequency__isnull=False, retention_time__isnull=False, level_of_identification__isnull=False).exists()
    def has_supporting_assets(self):
        return PrimarySupportingRel.objects.select_related('primary', 'supporting', 'primary__questionaire').filter(primary__questionaire=self.id).exists()
    def has_threats(self):
        return Threat_SA_REL.objects.filter(affected_supporting_asset__primary__questionaire=self.id).exists()
    def has_assessed_threats(self):
        assessed_threats = Threat_SA_REL.objects\
            .select_related('affected_supporting_asset', 'threat')\
            .filter(affected_supporting_asset__primary__questionaire_id=self.id, level_of_vulnerability__isnull=False, risk_source_capability__isnull=False)
        if assessed_threats.exists():
            return True
        return False
    def has_unassessed_threats(self):
        unassessed_threats = Threat_SA_REL.objects\
            .select_related('affected_supporting_asset', 'threat')\
            .filter(affected_supporting_asset__primary__questionaire_id=self.id, affected_supporting_asset__isnull=False, level_of_vulnerability__isnull=True, risk_source_capability__isnull=True)
        if unassessed_threats.exists():
            return True
        return False
    def has_assessed_risks(self):
        assessed_risks = Risk.objects.select_related('primary_asset_affected', 'risk_owner')\
            .prefetch_related('primary_asset_affected__primary_in_psrel__supporting__supporting_in_threatsarel',
                            'primary_asset_affected__primary_in_psrel__supporting__supporting_in_threatsarel__threat')\
            .filter(primary_asset_affected__questionaire=self.id, primary_asset_affected__primary_in_psrel__supporting__isnull=False,
            primary_asset_affected__primary_in_psrel__supporting__supporting_in_threatsarel__isnull=False, consequences__isnull=False, prejudicial_effects__isnull=False)
        if assessed_risks.exists():
            return True
        return False
    def has_unassessed_risks(self):
        unassessed_risks = Risk.objects.select_related('primary_asset_affected', 'risk_owner')\
            .prefetch_related('primary_asset_affected__primary_in_psrel__supporting__supporting_in_threatsarel',
                            'primary_asset_affected__primary_in_psrel__supporting__supporting_in_threatsarel__threat')\
            .filter(primary_asset_affected__questionaire=self.id, consequences__isnull=True, prejudicial_effects__isnull=True)
        if unassessed_risks.exists():
            return True
        return False
    def has_implemented_controls(self):
        implemented_controls = Threat_SA_REL.objects.select_related('affected_supporting_asset', 'threat')\
            .filter(affected_supporting_asset__primary__questionaire_id=self.id, control__isnull=False)
        if implemented_controls.exists():
            return True
        return False
    def has_unimplemented_controls(self):
        empty_controls = Threat_SA_REL.objects.select_related('affected_supporting_asset', 'threat')\
            .filter(affected_supporting_asset__primary__questionaire_id=self.id, control__isnull=True)
        if empty_controls.exists():
            return True
        return False
    def has_mitigated_risks(self):
        mitigated_risks = Risk.objects.select_related('primary_asset_affected', 'risk_owner')\
            .prefetch_related('risk_owner', 'primary_asset_affected__primary_in_psrel__supporting__supporting_in_threatsarel',
                            'primary_asset_affected__primary_in_psrel__supporting__supporting_in_threatsarel__threat')\
            .filter(primary_asset_affected__questionaire=self.id, primary_asset_affected__primary_in_psrel__supporting__isnull=False,
            primary_asset_affected__primary_in_psrel__supporting__supporting_in_threatsarel__isnull=False, risk_treatment__isnull=False, residual_risk__isnull=False)
        if mitigated_risks.exists():
            return True
        return False
    def has_unmitigated_risks(self):
        unmitigated_risks = Risk.objects.select_related('primary_asset_affected', 'risk_owner')\
            .prefetch_related('risk_owner', 'primary_asset_affected__primary_in_psrel__supporting__supporting_in_threatsarel',
                            'primary_asset_affected__primary_in_psrel__supporting__supporting_in_threatsarel__threat')\
            .filter(primary_asset_affected__questionaire=self.id, risk_treatment__isnull=True, residual_risk__isnull=True)
        if unmitigated_risks.exists():
            return True
        return False
    def has_privacy_targets(self):
        return PrivacyQuestionaireRel.objects.filter(questionaire=self.id).exists()
    def has_privacy_threats(self):
        return PrivacyThreatRel.objects.\
                prefetch_related('pqrel_in_pthreatrel', 'pqrel_in_pthreatrel__privacy_threat', 'pqrel_in_pthreatrel__affected_primary_assets', 'pqrel_in_pthreatrel__pthreatrel_in_pthreatcontrol__privacy_control').\
                select_related('privacy_q_rel').filter(privacy_q_rel__questionaire=self.id).exists()
    def has_privacy_controls(self):
        return PrivacyThreatControl.objects.select_related('privacy_threat_rel').filter(privacy_threat_rel__privacy_q_rel__questionaire=self.id).exists()

    def get_high_risks(self):
        high_risks = Risk.objects.filter(primary_asset_affected__questionaire=self.id,
                                            primary_asset_affected__primary_in_psrel__isnull=False,
                                            primary_asset_affected__primary_in_psrel__supporting__supporting_in_threatsarel__isnull=False,
                                            max_likelihood__gte=6, impact__gte=6).order_by('-risk_level').distinct()
        return high_risks

    def get_high_threats(self):
        high_threats = Threat_SA_REL.objects.select_related('affected_supporting_asset', 'threat').filter(affected_supporting_asset__questionaire=self.id, affected_supporting_asset__supporting_in_psrel__isnull=False)\
                                                .filter(Q(likelihood=7) | Q(likelihood=8)).order_by('-likelihood').distinct()
        return high_threats

    def get_risks(self):
        risks = Risk.objects.filter(primary_asset_affected__questionaire=self.id,
                                    primary_asset_affected__primary_in_psrel__supporting__isnull=False,
                                    primary_asset_affected__primary_in_psrel__supporting__supporting_in_threatsarel__isnull=False).order_by('-risk_level').distinct()
        return risks
    def get_threats(self):

        threats = Threat_SA_REL.objects\
                    .filter(affected_supporting_asset__supporting_in_psrel__primary__questionaire=self.id, affected_supporting_asset__isnull=False)\
                    .order_by('-likelihood').distinct()
        return threats

    @property
    def status(self):
        status = 0
        if self.has_sources():
            status += 10
        if self.has_primary_assets():
            status += 5
        if self.has_supporting_assets():
            status += 5
        if self.has_threats():
            status += 10
        if self.has_assessed_threats():
            status += 10
        if self.has_assessed_risks():
            status += 10
        if self.has_implemented_controls():
            status += 10
        if self.has_mitigated_risks():
            status += 10
        if self.has_privacy_targets():
            status += 10
        if self.has_privacy_threats():
            status += 10
        if self.has_privacy_controls():
            status += 10
        status = status
        return status

    class Meta:
        verbose_name = "Questionnaire"
        verbose_name_plural = "Questionnaires"

    def __unicode__(self):
        return '%s' %(self.description)


# Adds the intermediary model that connects User with questionaire to a ManyToMany Relationship
class Membership(models.Model):
    """ The Membership class defines the main storage point for Memberships.
        Each Membership has these fields:
        - **member** - defines a ManytoOne-Relationship of a Member to a User Profile.
        - **questionaire** - defines a ManytoOne-Relationship of a Membership to a Questionnaire .
        - **responsibility_in_dpia** - stores the responsibility that the user has for a particular membership to a questionnaire.
        - **owner** - defines if a member is the owner of a questionnaire or not.

        The Membership Meta class defines:
        - **unique_together** - sets the rule that a user's membership name is unique per questionnaire.
        - **verbose_name** - defines the Verbose name in singular.
        - **verbose_name_plural** - defines the Verbose name in plural.
    """

    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_membership")
    questionaire = models.ForeignKey(Questionaire, on_delete=models.CASCADE, related_name="q_in_membership")
    responsibility_in_dpia = models.CharField(max_length=256, blank=True, verbose_name="Responsibility in this Assessment")
    is_owner = models.BooleanField(default=False)

    class Meta:
        # no duplicates of a Relationship
        unique_together = (('member', 'questionaire'),)
        verbose_name = "Membership"
        verbose_name_plural = "Memberships"

    def __unicode__(self):
        #return "{}".format(self.is_owner)
        return "Membership of".format(self.questionaire.description) #(self.member.username,

class Question(models.Model):

    """ The Question class defines the main storage point for Pre-Assessment questions.
        Each Question has these fields:
        - **content** - stores the content of the question.
        - **criterion** - stores six options of criterions as choices. (Personal data, Data controller, Impact on rights, Timing, Nature of system, Legal basis.)
    """

    # CRITERION_CHOICES = (
    #     (1, "Personal data"),
    #     (2, "Data controller"),
    #     (3, "Impact on rights"),
    #     (4, "Timing"),
    #     (5, "Nature of system"),
    #     (6, "Legal basis"),
    #     )

    content = models.CharField(max_length=254, unique=True)
    # criterion = models.PositiveSmallIntegerField(choices=CRITERION_CHOICES, null=True, blank=True)

    # create new answer objects per each question; assign them to the user.
    def create_answer(self, user):
        new_answer_obj = Answer.objects.get_or_create(user=user, question=self, questionaire=None)

    def __unicode__(self):
        return '%s' %(self.content)


class Answer(models.Model):
    """ The Answer class defines the main storage point for Pre-Assessment answers.
        Each Answer has these fields:
        - **user** - defines a ManytoOne-Relationship of an Answer to a User Profile.
        - **questionaire** - defines a ManytoOne-Relationship of an Answer to a Questionnaire .
        - **question** - defines a ManytoOne-Relationship of an Answer to a Question.
        - **answer** - stores the answer, which is a boolean_field, i.e. it can be either yes or no.
    """

    BOOL_CHOICES = (
        (True, 'Yes'),
        (False, 'No'))

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    questionaire = models.ForeignKey(Questionaire, on_delete=models.CASCADE, blank=True, null=True, related_name="q_in_answer")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="question_in_answer")
    answer = models.BooleanField(choices=BOOL_CHOICES, blank=False, default=False)


    def __unicode__(self):
        return '(%s) %s' % (self.question, self.answer)

class SourceInventory(models.Model):
    """ The SourceInventory class defines the main storage point for Sources.
        Each Source has these fields:
        - **questionaire** - defines a ManytoOne-Relationship of a Source to a Questionnaire .
        - **name** - stores the name of the source.
        - **description** - stores the description of the source.
        - **source_type** - stores the type of the source.
        - **source_file** - stores a source file.
        - **uploaded_by** - defines a Relationship to the User Profile and stores the name of that user as the one who uploaded the source_file.
        - **purpose** - stores the purpose of the source.
    """

    questionaire = models.ForeignKey(Questionaire, on_delete=models.CASCADE, related_name="q_in_source")
    name = models.CharField(max_length=256, blank=False)
    description = models.CharField(max_length=256, blank=False)
    source_type = models.CharField(max_length=256, blank=False)
    source_file = models.FileField(null=True, blank=True, upload_to='source_file_uploads/%Y/%m/%d/')
    uploaded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=256, blank=False)

    class Meta:
        verbose_name = "Source"
        verbose_name_plural = "Sources"


    def __unicode__(self):
        return '%s' %(self.name)


## Import SGAM XML Files MODEL ##
class SgamXml(models.Model):
    questionaire = models.ForeignKey(Questionaire, on_delete=models.CASCADE)
    xml_file = models.FileField(null=True, blank=False, upload_to='sgam_file_uploads/%Y/%m/%d/')

    def __unicode__(self):
        return '%s' %(self.xml_file.name)
## / End SGAM Model

class UseCase(models.Model):
    """ The UseCase class defines the main storage point for Use Cases.
        Each Use Case has these fields:
        - **questionaire** - defines a ManytoOne-Relationship of a Use Case to a Questionnaire .
        - **name** - stores the name of the source.
        - **description** - stores the description of the use case.
        - **domain** - stores the domain of the use case.
        - **business_goal** - stores the business goal of the use case.
    """

    questionaire = models.ForeignKey(Questionaire, on_delete=models.CASCADE, related_name="q_in_usecase")
    name = models.CharField(max_length=256, blank=False)
    domain = models.CharField(max_length=256, blank=False)
    description = models.TextField(max_length=500, blank=False)
    business_goal = models.CharField(max_length=256, blank=False)

    class Meta:
        verbose_name = "Use case"
        verbose_name_plural = "Use cases"

    def __unicode__(self):
        return '%s' %(self.name)


class Actor(models.Model):
    """ The Actor class defines the main storage point for Actors.
        Each Actor has these fields:
        - **usecase** - defines a ManytoOne-Relationship of an Actor to a Use Case.
        - **name** - stores the name of the actor.
        - **description** - stores the description of the actor.
        - **actor_type** - stores the type of actor.
    """

    usecase = models.ForeignKey(UseCase, on_delete=models.CASCADE, null=True, blank=True, related_name="usercase_in_actor")
    name = models.CharField(max_length=256, blank=False)
    description = models.CharField(max_length=256, blank=False)
    actor_type = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        # unique_together = (('usecase', 'name'),)
        verbose_name = "Actor"
        verbose_name_plural = "Actors"

    def __unicode__(self):
        return '%s' %(self.name)


BOOL_CHOICES = (
    (True, 'Yes'),
    (False, 'No'))

LEVEL_CHOICES = (
    (1, "Negligible"),
    (2, "Limited"),
    (3, "Significant"),
    (4, "Maximum"),
    )

# create custom manager
class PrimaryRelatedObjectsManager(models.Manager):
    def get_queryset(self):
        return super(PrimaryRelatedObjectsManager, self).get_queryset()\
        .select_related('questionaire', 'data_subjects')\
        .prefetch_related('primary_in_psrel', 'primary_in_psrel', 'primary_in_psrel__supporting')

class Primary(models.Model):
    """ The Primary class defines the main storage point for Primary Assets.
        Each Primary has these fields:
        - **questionaire** - defines a ManytoOne-Relationship of a primary asset to a Questionnaire.
        - **name** - stores the name of the primary asset.
        - **reading_frequency** - stores the reading frequency of the primary asset.
        - **retention_time** - stores the retention time of the primary asset.
        - **data_subjects** - defines a ManytoOne-Relationship of a primary asset to an Actor.
        - **required** - defines if a primary asset is required or not.
        - **level_of_identification** - stores the level of identification of the primary asset.

        The Primary Meta class defines:
        - **unique_together** - sets the rule that a primary asset's name is unique per questionnaire.
    """

    questionaire = models.ForeignKey(Questionaire, on_delete=models.CASCADE, null=True, blank=True, related_name="q_in_primary")
    name = models.CharField(max_length=256, blank=False, null=True, verbose_name="Information exchanged")
    reading_frequency = models.CharField(max_length=256, blank=False)
    retention_time = models.CharField(max_length=256, blank=False)
    data_subjects = models.ForeignKey(Actor, null=True, related_name="actor", verbose_name="Data Subject")
    required = models.NullBooleanField(choices=BOOL_CHOICES, blank=False, null=True, default=True) #default=None
    level_of_identification = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, null=True, blank=False, validators=[MinValueValidator(0),
                                      MaxValueValidator(4)])

    is_imported = models.BooleanField(blank=True, default=False)
    objects = PrimaryRelatedObjectsManager()

    class Meta:
        unique_together = (('questionaire', 'name'),)
        verbose_name = "Primary Asset"
        verbose_name_plural = "Primary Assets"

    def __unicode__(self):
        return u"%s" %(self.name)


class Process(models.Model):
    """ The Process class defines the main storage point for Processes.
        Each Process has these fields:
        - **usecase** - defines a ManytoOne-Relationship of a Process to a Use Case.
        - **step_nr** - stores the step number of the process.
        - **description** - stores the description of the process.
        - **information_producer** - defines a ManytoOne-Relationship of an actor to the process.
        - **information_receiver** - defines a ManytoOne-Relationship of an actor to the process.
        - **information_exchanged** - defines a ManytoOne-Relationship of a primary asset to the process.
    """

    usecase = models.ForeignKey(UseCase, on_delete=models.CASCADE, related_name="process")
    step_nr = models.IntegerField(null=True, blank=False)
    description = models.CharField(max_length=256, null=True, blank=False, verbose_name="Description of Process")
    information_producer = models.ForeignKey(Actor, null=True, blank=False, related_name="producer")
    information_receiver = models.ForeignKey(Actor, null=True, blank=False, related_name="receiver")
    information_exchanged = models.ForeignKey(Primary, null=True, blank=False, on_delete=models.CASCADE, related_name="primary")


    class Meta:
        verbose_name = "Process"
        verbose_name_plural = "Processes"

    def __unicode__(self):
        return '%s' %(self.description)

    def get_absolute_url(self):
        return reverse("process", kwargs={"id": self.id})

# create custom manager
class SupportingRelatedObjectsManager(models.Manager):
    def get_queryset(self):
        return super(SupportingRelatedObjectsManager, self).get_queryset()\
        .select_related('questionaire').prefetch_related('supporting_in_threatsarel', 'supporting_in_threatsarel__threat')

class Supporting(models.Model):
    """ The Supporting class defines the main storage point for Supporting Assets.
        Each Supporting Asset has these fields:
        - **supporting_type** - stores the type of the supporting asset.
        - **description** - stores the description of the supporting asset.
        - **primary** - defines a ManytoMany-Relationship of a Primary Asset to the supporting asset through an intermediary table called "PrimarySupportingRel".
        - **questionaire** - defines a ManytoOne-Relationship of a questionnaire to the process.
    """

    supporting_asset_types = (
        ('Hardware', 'Hardware'),
        ('Software', 'Software'),
        ('Network Equipment', 'Network Equipment'),
        ('Communication', 'Communication'),
        ('Network', 'Network'),
        ('People', 'People'),
        ('Paper transmission channel', 'Paper transmission channel'),
    )
    supporting_type = models.CharField(max_length=256, choices=supporting_asset_types, blank=False, null=True, verbose_name="Supporting Asset Type")
    description = models.CharField(max_length=255, blank=False, null=True)
    ## SGAM Component EAID
    ea_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="EAID")
    ## foreign keys
    primary = models.ManyToManyField(Primary, through="PrimarySupportingRel", related_name="primaries_in_supporting_obj")
    questionaire = models.ForeignKey(Questionaire, null=True, blank=True, on_delete=models.CASCADE, related_name="q_in_supporting")
    objects = SupportingRelatedObjectsManager()

    class Meta:
        unique_together = (('questionaire', 'description'), ('questionaire', 'ea_id'),)
        verbose_name = "Supporting Asset"
        verbose_name_plural = "Supporting Assets"

    def __unicode__(self):
        return u"%s" %(self.description)


class PrimarySupportingRel(models.Model):
    """ The PrimarySupportingRel class defines the M2M-intermediary table between a Primary Asset and a Supporting asset.
        Each PrimarySupportingRel has 2 fields:
        - **primary** - defines a ManytoOne-Relationship of the intermediary table to a primary asset.
        - **supporting** - defines a ManytoOne-Relationship of the intermediary table to a supporting asset.
    """

    primary = models.ForeignKey(Primary, on_delete=models.CASCADE, verbose_name="Primary Asset", related_name="primary_in_psrel")
    supporting = models.ForeignKey(Supporting, on_delete=models.CASCADE, verbose_name="Supporting Asset", related_name="supporting_in_psrel")

    class Meta:
        verbose_name = "Supporting Asset of Primary Asset"
        verbose_name_plural = "Supporting Assets of Primary Asset"

    def __unicode__(self):
        # return "PSRel"
        return u'PSRel between {} and {}'.format(self.primary, self.supporting)



class Threat(models.Model):
    """ The Threat class defines the main storage point for Threats.
        Each Threat has these fields:
        - **name** - stores the name of the threat.
        - **description** - stores the description of the supporting threat.
        - **motivation** - stores the motivation of the supporting threat.
        - **type_of_jeopardy** - stores the jeopardy type of the threat.
        - **supporting_asset_types** - stores the types of the supporting asset.
        - **supporting** - defines a ManytoMany-Relationship of a threat to the supporting asset through an intermediary table called "Threat_SA_REL".
    """

    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(max_length=255, null=True, blank=False)
    motivation = models.TextField(max_length=255, null=True, blank=False)
    jeopardy_types = (
        ('Confidentiality', 'Confidentiality'),
        ('Integrity', 'Integrity'),
        ('Availability', 'Availability'),
    )
    type_of_jeopardy = models.CharField(max_length=256, choices=jeopardy_types, null=True,)

    supporting_asset_types = (
        ('Hardware', 'Hardware'),
        ('Software', 'Software'),
        ('Network Equipment', 'Network Equipment'),
        ('Network', 'Network'),
        ('People', 'People'),
        ('Paper transmission channel', 'Paper transmission channel'),
    )
    supporting_asset_type = models.CharField(max_length=256, choices=supporting_asset_types, verbose_name="Type of Supporting Asset Affected by this Threat")
    ## rels
    supporting = models.ManyToManyField(Supporting, through="Threat_SA_REL", related_name="supportings_in_threat")

    class Meta:
        verbose_name = "Threat"
        verbose_name_plural = "Threats"

    def __unicode__(self):
        return u"%s" %(self.name)


# create custom manager
class ThreatSaRelRelatedObjectsManager(models.Manager):
    def get_queryset(self):
        return super(ThreatSaRelRelatedObjectsManager, self).get_queryset()\
        .select_related('affected_supporting_asset', 'threat')

class Threat_SA_REL(models.Model):
    """ The Threat_SA_REL class defines the M2M-intermediary table between a Threat and a Supporting asset.
        Each Threat_SA_REL has these fields:
        - **threat** - defines a ManytoOne-Relationship of the intermediary table to a threat.
        - **affected_supporting_asset** - defines a ManytoOne-Relationship of the intermediary table to a supporting asset.
        - **level_of_vulnerability** - stores the level of vulnerability of the threat-supporting_asset-relationship.
        - **risk_source_capability** - stores the risk source capability of the threat-supporting_asset-relationship.
        - **control** - stores the control of the threat-supporting_asset-relationship.
        - **likelihood** - stores the likelihood of the threat-supporting_asset-relationship, which is calculates as the sum of the level_of_vulnerability and risk_source_capability.
    """


    level_of_vulnerability = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, null=True, blank=False, verbose_name="Level of vulnerability")
    risk_source_capability = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, null=True, blank=False, verbose_name="Risk source capability")
    affected_supporting_asset = models.ForeignKey(Supporting, on_delete=models.CASCADE, blank=False, related_name="supporting_in_threatsarel")
    threat = models.ForeignKey(Threat, on_delete=models.CASCADE, related_name="threat_in_threatsarel")
    control = models.TextField(max_length=255, null=True, blank=False)
    likelihood = models.IntegerField(null=False, default=0, blank=True)
    objects = ThreatSaRelRelatedObjectsManager()

    class Meta:
        verbose_name = "Threat affecting Supporting Asset"
        verbose_name_plural = "Threats affecting Supporting Assets"

    def __unicode__(self):
        return u'({})'.format(self.threat)

# create custom manager
class RiskRelatedObjectsManager(models.Manager):
    def get_queryset(self):
        return super(RiskRelatedObjectsManager, self).get_queryset()\
        .select_related('primary_asset_affected', 'risk_owner')

        # .prefetch_related('primary_asset_affected__primary_in_psrel__supporting__supporting_in_threatsarel',
        #                 'primary_asset_affected__primary_in_psrel__supporting__supporting_in_threatsarel__threat')

class Risk(models.Model):
    """ The Risk class defines the main storage point for Risks.
        Each Risk has these fields:
        - **risk_owner** - stores the risk owner of the risk.
        - **prejudicial_effects** - stores the prejudicial effects' value of the risk.
        - **risk_treatment** - stores the risk treatment of the risk.
        - **residual_risk** - stores the residual risk of the risk.
        - **control** - stores the control of the risk.
        - **primary_asset_affected** - defines a ManytoOne-Relationship of a risk to a primary asset.
        - **risk_level** - stores the risk level of the risk, which is the sum of the prejudicial_effects of the risk, level_of_identification of the primary asset, the level_of_vulnerability and risk_source_capability of the supporting_asset-threat relationship.
        - **max_likelihood** - stores the maximum value of the likelihood of the threats that are related to the risk. This function is defined in the views.

    """

    risk_owner = models.ForeignKey(Actor, on_delete=models.CASCADE, blank=True, null=True, related_name="risk_owner")
    prejudicial_effects = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, null=True, blank=False, validators=[MinValueValidator(0),
                                      MaxValueValidator(4)])
    risk_treatment = models.CharField(max_length=255, null=True, blank=True)
    residual_risk = models.CharField(max_length=255, null=True, blank=True)

    consequences = models.TextField(max_length=255, null=True, blank=True)
    control = models.TextField(max_length=255, null=True, blank=True)

    # RELs
    primary_asset_affected = models.ForeignKey(Primary, on_delete=models.CASCADE, blank=False, related_name="primary_in_risk")
    jeopardy_types = (
        ('Confidentiality', 'Confidentiality'),
        ('Integrity', 'Integrity'),
        ('Availability', 'Availability'),
    )
    type_of_jeopardy = models.CharField(max_length=255, choices=jeopardy_types, blank=True)
    risk_level = models.IntegerField(null=False, default=0, blank=True)
    max_likelihood = models.IntegerField(null=False, default=0, blank=True)
    impact = models.IntegerField(null=False, default=0, blank=True)
    objects = RiskRelatedObjectsManager()

    class Meta:
        verbose_name = "Risk"
        verbose_name_plural = "Risks"

    def __unicode__(self):
        return "{} risk".format(self.type_of_jeopardy)



## Privacy Targets and Threats
class PrivacyControl(models.Model):
    """ The PrivacyControl class defines the main storage point for Privacy Controls.
        Each Privacy Control has 1 field:
        - **name** - stores the name of the privacy control.
    """
    name = models.CharField(max_length=255, blank=False, null=True, unique=True)

    def __unicode__(self):
        return u"%s" %(self.name)


class PrivacyThreat(models.Model):
    """ The PrivacyThreat class defines the main storage point for Privacy Threats.
        Each Privacy Threat has these fields:
        - **name** - stores the name of the privacy threat.
        - **description** - stores the description of the privacy threat.
        - **privacy_controls** - defines a ManytoMany-Relationship of privacy threats to privacy controls.
    """

    name = models.CharField(max_length=255, null=True, blank=False, unique=True)
    description = models.TextField(max_length=255, null=True, blank=False)
    privacy_controls = models.ManyToManyField(PrivacyControl, blank=True, verbose_name="Privacy Controls", related_name="pcontrols_in_pthreat", help_text="Check/Uncheck to add or remove Privacy Controls")

    class Meta:
        verbose_name = "Privacy Threat"
        verbose_name_plural = "Privacy Threats"

    def __unicode__(self):
        return u"%s" %(self.name)

class PrivacyTarget(models.Model):
    """ The PrivacyTarget class defines the main storage point for Privacy Targets.
        Each Privacy Target has these fields:
        - **name** - stores the name of the privacy target.
        - **description** - stores the description of the privacy target.
        - **questionaire** - defines a ManytoMany-Relationship of privacy targets to questionnaires through an intermediary table called "PrivacyQuestionaireRel".
        - **threats** - defines a ManytoMany-Relationship of privacy targets to threats.
    """
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    description = models.TextField(max_length=255, null=True, blank=True)
    questionaire = models.ManyToManyField(Questionaire, blank=True, through="PrivacyQuestionaireRel")
    threats = models.ManyToManyField(PrivacyThreat, blank=True, related_name="threats_in_ptarget")

    class Meta:
        verbose_name = "Privacy Target"
        verbose_name_plural = "Privacy Targets"

    def __unicode__(self):
        return u"%s" %(self.name)

# create custom manager
class PQRelRelatedObjectsManager(models.Manager):
    def get_queryset(self):
        return super(PQRelRelatedObjectsManager, self).get_queryset()\
        .select_related('questionaire', 'privacy_target')\
        .prefetch_related('pqrel_in_pthreatrel__privacy_threat',
                        'pqrel_in_pthreatrel__affected_primary_assets',
                        'pqrel_in_pthreatrel__pthreatrel_in_pthreatcontrol__privacy_control')



class PrivacyQuestionaireRel(models.Model):
    """ The PrivacyQuestionaireRel class defines the M2M-intermediary table between a PrivacyTarget and a Questionnaire.
        Each PrivacyQuestionaireRel has these fields:
        - **questionaire** - defines a ManytoOne-Relationship to a questionaire.
        - **privacy_target** - defines a ManytoOne-Relationship to a privacy target.
        - **privacy_threats** - defines a ManytoMany-Relationship of PrivacyQuestionaireRel intermediary table to privacy threats through an intermediary table called "PrivacyThreatRel".
    """

    questionaire = models.ForeignKey(Questionaire, on_delete=models.CASCADE, related_name="q_in_pqrel")
    privacy_target = models.ForeignKey(PrivacyTarget, on_delete=models.CASCADE, related_name="ptarget_in_pqrel")
    privacy_threats = models.ManyToManyField(PrivacyThreat, blank=True, through="PrivacyThreatRel", related_name="pthreats_in_pqrel")
    objects = PQRelRelatedObjectsManager()

    class Meta:
        verbose_name = "Privacy Target Rel to Questionnaire"
        verbose_name_plural = "Privacy Target Rel to Questionnaires"

    def __unicode__(self):
        return u"Privacy target of {}".format(self.questionaire)



class PrivacyThreatRel(models.Model):
    """ The PrivacyThreatRel class defines the M2M-intermediary table between a PrivacyQuestionaireRel and a privacy threats.
        Each PrivacyThreatRel has these fields:
        - **privacy_threat** - defines a ManytoOne-Relationship to a privacy threat.
        - **privacy_q_rel** - defines a ManytoOne-Relationship to a PrivacyQuestionaireRel intermediary table.
        - **affected_primary_assets** - defines a ManytoMany-Relationship of PrivacyThreatRel to primary assets.
        - **controls** - defines a ManytoMany-Relationship of PrivacyThreatRel intermediary table to privacy controls through an intermediary table called "PrivacyThreatControl".
    """

    privacy_threat = models.ForeignKey(PrivacyThreat, on_delete=models.CASCADE, related_name="pthreat_in_pthreatrel")
    privacy_q_rel = models.ForeignKey(PrivacyQuestionaireRel, on_delete=models.CASCADE, related_name="pqrel_in_pthreatrel")
    affected_primary_assets = models.ManyToManyField(Primary, blank=True, verbose_name="Affected Primary Assets", related_name="primary_in_pthreatreal", help_text="Check/Uncheck to add or remove Primary Assets")
    controls = models.ManyToManyField(PrivacyControl, blank=True, through="PrivacyThreatControl", related_name="pcontrols_in_pthreatreal")

    class Meta:
        verbose_name = "Privacy Threat that jeopardizes Privacy Target"
        verbose_name_plural = "Privacy Threats that jeopardize Privacy Target"

    def __unicode__(self):
        return u"Privacy threat" #of {}".format(self.privacy_q_rel)


class PrivacyThreatControl(models.Model):
    """ The PrivacyThreatControl class defines the M2M-intermediary table between PrivacyThreatRels and Privacy Threat Controls.
        Each PrivacyThreatControl has these fields:
        - **privacy_threat_rel** - defines a ManytoOne-Relationship to a PrivacyThreatRel intermediary table.
        - **privacy_control** - defines a ManytoOne-Relationship to privacy controls.
    """

    privacy_threat_rel = models.ForeignKey(PrivacyThreatRel, on_delete=models.CASCADE, related_name="pthreatrel_in_pthreatcontrol")
    privacy_control = models.ForeignKey(PrivacyControl, on_delete=models.CASCADE, related_name="pcontrol_in_pthreatcontrol")

    class Meta:
        verbose_name = "Privacy Control applied to Privacy Threat"
        verbose_name_plural = "Privacy Controls applied to Privacy Threat"


    def __unicode__(self):
        return "(%s) %s" % (self.privacy_threat_rel, self.privacy_control)




## signals to create and save user profile, active/deactive user after registration, and delete the user when the profile is deleted.
# Creates UserProfile
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

# deactivates the User that is being created
@receiver(pre_save, sender=User)
def user_activation(sender, instance, **kwargs):
    """ The user_activation function sends a pre-signal to deactivate a newly registered user, so they cannot access the tool without being activated by the administrators.
    """
    if instance.id is None:
        # user is being created
        instance.is_active = True # for now it's set to true, i.e. any newly registered user can login after registration.

# deletes User when UserProfile is deleted
def delete_user(sender, instance=None, **kwargs):
    """ The delete_user function deletes a User when the Profile of that user is deleted.
    """
    try:
        instance.user
    except User.DoesNotExist:
        pass
    else:
        instance.user.delete()
signals.post_delete.connect(delete_user, sender=UserProfile)




## Revision declaration of models
reversion.register(Questionaire, follow=["q_in_membership", "q_in_answer", "q_in_source", "q_in_primary", "q_in_pqrel"])
reversion.register(Answer, follow=['questionaire'])
reversion.register(Membership, follow=["questionaire"])
reversion.register(SourceInventory, follow=["questionaire"])
reversion.register(Actor)

reversion.register(Primary, follow=["questionaire", "primary_in_psrel", "primary_in_risk"])#, "primary_in_psrel", "primary_in_risk"])
reversion.register(Supporting, follow=["supporting_in_psrel", "supporting_in_threatsarel"])
reversion.register(PrimarySupportingRel, follow=["supporting", "primary"])
reversion.register(Threat, follow=["threat_in_threatsarel"])
reversion.register(Threat_SA_REL, follow=["affected_supporting_asset", "threat"])

reversion.register(Risk, follow=["primary_asset_affected"])

reversion.register(PrivacyTarget, follow=["ptarget_in_pqrel"])
reversion.register(PrivacyQuestionaireRel, follow=["questionaire", "pqrel_in_pthreatrel"])
reversion.register(PrivacyThreat, follow=["pthreat_in_pthreatrel"])
reversion.register(PrivacyThreatRel, follow=["privacy_q_rel", "affected_primary_assets", "pthreatrel_in_pthreatcontrol"])
reversion.register(PrivacyControl, follow=["pcontrol_in_pthreatcontrol"])
reversion.register(PrivacyThreatControl, follow=["privacy_threat_rel"])
