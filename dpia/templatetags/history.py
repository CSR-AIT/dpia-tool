import os
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django import template
from reversion.models import Version
from django.core.urlresolvers import resolve

from dpia.models import *
register = template.Library()


@register.simple_tag()
def get_history(q_id):
    versions = Version.objects.prefetch_related('revision', 'revision__user').get_for_object_reference(Questionaire, q_id, model_db=None)[:4]
    return versions

@register.simple_tag
def nav_active(request, url):
    url_name = resolve(request.path).url_name
    if url_name == url:
        return "active"
    return ""
