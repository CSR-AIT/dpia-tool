#!/usr/bin/env python
# coding: utf8

from django.contrib.auth import (
    authenticate, REDIRECT_FIELD_NAME, get_user_model,
    login, logout, update_session_auth_hash
)
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

from django.conf import settings
from django.conf.urls import url

from django.core import serializers
from django.core.urlresolvers import reverse, reverse_lazy, resolve
from django.core.signals import request_finished, request_started
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.core.files.storage import FileSystemStorage
from django.core.cache import cache # This is the memcache


# from django.utils.deprecation import RemovedInDjango110Warning
from django.utils.encoding import force_text, smart_str
from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.utils.six.moves.urllib.parse import urlparse, urlunparse
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

from django.shortcuts import resolve_url, render_to_response, redirect, render, get_object_or_404

from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, QueryDict, HttpResponseForbidden

from django.template.response import TemplateResponse
from django.template import RequestContext, Context
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters


from django.db.models.signals import pre_delete, post_delete
from django.db import IntegrityError, transaction
from django.db.models import Max, Min, F, FloatField, Sum, Prefetch, Q
from django.db import connection

from django.template.loader import get_template, render_to_string
from django.template.context_processors import csrf

from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import TemplateView
from django.views.generic import CreateView, UpdateView

from django.forms import modelformset_factory, inlineformset_factory, BaseFormSet, formset_factory
from django import template, forms

## Python modules
from wsgiref.util import FileWrapper
from mimetypes import MimeTypes
import mimetypes, os
import urllib2
import time
import pdb
import time
import cStringIO as StringIO
import os.path
from collections import namedtuple
from datetime import datetime

# app imports
from dpia.models import *
from dpia.forms import *
from dpia.decorators import *
from reversion.models import Version

## PDF Generator // reportlab
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, BaseDocTemplate, Frame, PageTemplate, Paragraph, PageBreak
from reportlab.platypus.flowables import Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, StyleSheet1, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch

## GENERATE WORD DOCX
from docx import *
from docx.shared import Inches, Cm, Pt


# shortcut function to save the history of CRUD actions.
def save_revision_meta(user, q, comment):
    reversion.set_user(user)
    membership = get_object_or_404(Membership, questionaire=q, is_owner=True)
    reversion.add_meta(VersionOwner, owner_id=membership.member.id)
    reversion.set_comment(comment)

    
