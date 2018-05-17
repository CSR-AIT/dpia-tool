"""dpia_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from dpia.views import  (
    deleted_questionnaires, user_login, register, dashboard, profile, profile_edit, password_change, user_logout,
    pre_assessment, pre_assessment_confirmation, pre_assessment_update
)
from dpia.forms import CheckResetEmailForm, CheckPasswordChangeForm, ResetPasswordChangeForm


urlpatterns = [
    # admin.
    url(r'^admin/', admin.site.urls),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # dashboard.
    url(r'^dashboard/$', dashboard, name='dashboard'),
    # accounts.
    url(r'^$', user_login, name='login'),
    url(r'^register/$', register, name='register'),
    url(r'^profile/$', profile, name='profile'),
    url(r'^profile/update/$', profile_edit,  name='profile_edit'),
    url(r'^logout/$', user_logout, name="logout"),

    # questionnaire.
    url(r'^questionnaire/', include('dpia.urls')),
    url(r'^deleted-questionnaires/$', deleted_questionnaires, name='deleted_questionnaires'),
    ### Pre-Assessment
    url(r'^pre-assessment/$', pre_assessment, name='pre_assessment'),
    url(r'^pre-assessment/confirmation/$', pre_assessment_confirmation, name='pre_assessment_confirmation'),
    url(r'^questionnaire/(?P<q_id>[0-9]+)/pre-assessment/update/$', pre_assessment_update, name='pre_assessment_update'),

    ### RESET PASSWORD
    url(r'^password/reset/$', auth_views.password_reset, {'template_name': 'accounts/password_settings/password_reset.html', 'password_reset_form': CheckResetEmailForm}, name='password_reset'),
    url(r'^password/reset/done/$', auth_views.password_reset_done, {'template_name': 'accounts/password_settings/password_reset_done.html'}, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, {'template_name': 'accounts/password_settings/password_reset_confirm.html', 'set_password_form': ResetPasswordChangeForm}, name='password_reset_confirm'),
    url(r'^password/reset/complete/$', auth_views.password_reset_complete, {'template_name': 'accounts/password_settings/password_reset_complete.html'}, name='password_reset_complete'),
    ### CHANGE PASSWORD
    url(r'^password/change/$', password_change, name='password_change'),

    # url(r'^accounts/password/change/$', auth_views.password_change, {'template_name': 'accounts/password_settings/password_change.html', 'password_change_form': CheckPasswordChangeForm}, name='password_change'),
    # url(r'^accounts/password/change/done/$', auth_views.password_change_done, {'template_name': 'accounts/password_settings/password_change_done.html'}, name='password_change_done'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
