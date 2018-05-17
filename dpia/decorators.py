from django.contrib.auth.models import User
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.db.models import Max, Min, F, FloatField, Sum, Prefetch, Q
from dpia.models import *

# decorator for owner authorization
def auth_required(function):
    def wrap(request, *args, **kwargs):
        membership = get_object_or_404(Membership, questionaire=kwargs['q_id'], member=request.user)
        if membership.is_owner:
            return function(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You are not allowed to perform this action!")
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

## decorators to see if each step is completed
def pre_assessment_required(function):
    def wrap(request, *args, **kwargs):
        answers = Answer.objects.filter(user=request.user, questionaire=None)
        if answers.exists():
            return function(request, *args, **kwargs)
        else:
            messages.warning(request, 'Complete Pre-Assessment to activate the next step.')
            return redirect(reverse('pre_assessment'))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def primary_assets_required(function):
    def wrap(request, *args, **kwargs):
        q = get_object_or_404(Questionaire, id=kwargs['q_id'], q_in_membership__member=request.user)
        if q.has_primary_assets():
            return function(request, *args, **kwargs)
        else:
            messages.warning(request, 'Add and fill out the primary assets to activate the next step.')
            return redirect(reverse('primary_list', args=[q.id]))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def supporting_assets_required(function):
    def wrap(request, *args, **kwargs):
        q = get_object_or_404(Questionaire, id=kwargs['q_id'], q_in_membership__member=request.user)
        if q.has_supporting_assets():
            return function(request, *args, **kwargs)
        else:
            messages.warning(request, 'Add supporting assets to activate the next step.')
            return redirect(reverse('primary_list', args=[q.id]))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def threats_required(function):
    def wrap(request, *args, **kwargs):
        q = get_object_or_404(Questionaire, id=kwargs['q_id'], q_in_membership__member=request.user)
        if q.has_threats():
            return function(request, *args, **kwargs)
        else:
            messages.warning(request, 'Add threats to activate the next step.')
            return redirect(reverse('threat_identification', args=[q.id]))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def threat_assessment_required(function):
    def wrap(request, *args, **kwargs):
        q = get_object_or_404(Questionaire, id=kwargs['q_id'], q_in_membership__member=request.user)
        if q.has_unassessed_threats():
            messages.warning(request, 'Assess likelihood of threats to activate the next step.')
            return redirect(reverse('threat_assessment', args=[q.id]))
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def delete_nothreat_risks(function):
    def wrap(request, *args, **kwargs):
        empty_risks = Risk.objects\
                .filter(primary_asset_affected__questionaire=kwargs['q_id'],\
                primary_asset_affected__primary_in_psrel__supporting__supporting_in_threatsarel__isnull=True)
        if empty_risks:
            empty_risks.delete()
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def risk_assessment_required(function):
    def wrap(request, *args, **kwargs):
        q = get_object_or_404(Questionaire, id=kwargs['q_id'], q_in_membership__member=request.user)
        if q.has_unassessed_risks():
            messages.warning(request, 'Assess impact of risks to activate the next step.')
            return redirect(reverse('risk_assessment', args=[q.id]))
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def threat_controls_required(function):
    def wrap(request, *args, **kwargs):
        q = get_object_or_404(Questionaire, id=kwargs['q_id'], q_in_membership__member=request.user)
        if q.has_unimplemented_controls():
            messages.warning(request, 'Add threat controls to activate the next step.')
            return redirect(reverse('threat_controls', args=[q.id]))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def privacy_targets_required(function):
    def wrap(request, *args, **kwargs):
        q = get_object_or_404(Questionaire, id=kwargs['q_id'], q_in_membership__member=request.user)
        if q.has_privacy_targets():
            return function(request, *args, **kwargs)
        else:
            messages.warning(request, 'Add privacy targets to activate the next step.')
            return redirect(reverse('privacy_target_identification', args=[q.id]))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def privacy_threats_required(function):
    def wrap(request, *args, **kwargs):
        q = get_object_or_404(Questionaire, id=kwargs['q_id'], q_in_membership__member=request.user)
        if q.has_privacy_threats():
            return function(request, *args, **kwargs)
        else:
            messages.warning(request, 'Add privacy threats to activate the next step.')
            return redirect(reverse('privacy_threat_identification', args=[q.id]))

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def privacy_controls_required(function):
    def wrap(request, *args, **kwargs):
        q = get_object_or_404(Questionaire, id=kwargs['q_id'], q_in_membership__member=request.user)
        if q.has_privacy_controls():
            return function(request, *args, **kwargs)
        else:
            messages.warning(request, 'Add privacy controls to activate the next step.')
            return redirect(reverse('privacy_control_implementation', args=[q.id]))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
## ./end steps completion decorators
