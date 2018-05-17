import os
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django import template
from reversion.models import Version
from django.core.urlresolvers import resolve

from dpia.models import *
register = template.Library()

@register.simple_tag()
def is_authorized(q, user):
    membership = get_object_or_404(Membership.objects.select_related('member', 'questionaire'), questionaire=q, member=user)
    if membership.is_owner:
        return True
    return False


@register.filter
def to_class_name(obj):
    return obj.__class__.__name__
