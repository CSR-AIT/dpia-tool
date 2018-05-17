from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import include, url
from django.contrib import admin
from dpia import views
from django_downloadview import ObjectDownloadView
from dpia.models import SourceInventory

# fuction to serve source files.
download_file = ObjectDownloadView.as_view(model=SourceInventory, file_field='source_file')

urlpatterns = [
    ### QUESTIONNAIRE URLS
    ## Qs
    url(r'^add/$', views.q_add, name='q_add'),
    url(r'^(?P<q_id>[0-9]+)/edit/?$', views.q_edit, name='q_edit'),
    url(r'^(?P<q_id>[0-9]+)/delete/?$', views.q_delete, name='q_delete'),
    ## Members
    url(r'^(?P<q_id>[0-9]+)/members/?$', views.members, name='members'),
    url(r'^(?P<q_id>[0-9]+)/members/add/?$', views.member_add, name='member_add'),
    url(r'^(?P<q_id>[0-9]+)/member/(?P<membership_id>[0-9]+)/edit/?$', views.member_edit, name='member_edit'),
    url(r'^(?P<q_id>[0-9]+)/member/(?P<membership_id>[0-9]+)/delete/?$', views.member_delete, name='member_delete'),
    ## Sources
    url(r'^(?P<q_id>[0-9]+)/sources/$', views.sources, name='sources'),
    url(r'^(?P<q_id>[0-9]+)/sources/add/$', views.add_source, name='add_source'),
    url(r'^source/(?P<source_id>[0-9]+)/edit/?$', views.edit_source, name='edit_source'),
    url(r'^source/(?P<source_id>[0-9]+)/delete/?$', views.delete_source, name='delete_source'),
    url(r'^(?P<pk>[0-9]+)/download-souce-file/$', download_file, name='download_source_file'),
    url(r'^(?P<q_id>[0-9]+)/(?P<source_id>[0-9]+)/delete-source-file/$', views.source_file_delete, name='delete_source_file'),

    # url(r'^(?P<q_id>[0-9]+)/download/(?P<file_url>.+)$', views.download_source_file, name='download_source_file'),
    ## Use cases
    url(r'^(?P<id>[0-9]+)/use-cases/$', views.usecases, name='usecases'),
    url(r'^(?P<id>[0-9]+)/use-case/add/$', views.add_usecase, name='add_usecase'),
    url(r'^use-case/(?P<id>[0-9]+)$', views.usecase_scenario, name='usecase_details'),
    url(r'^use-case/(?P<id>[0-9]+)/edit/?$', views.edit_usecase, name='edit_usecase'),
    url(r'^use-case/(?P<id>[0-9]+)/delete/?$', views.delete_usecase, name='delete_usecase'),
    url(r'^process/(?P<id>[0-9]+)/delete/?$', views.process_delete, name='process_delete'),
    ## Actors
    url(r'^use-case(?P<id>[0-9]+)/actor/add/$', views.actor_add, name='actor_add'),

    ## Primary assets
    # url(r'^(?P<q_id>[0-9]+)/primary-assets/add/$', views.primary_add, name='primary_add'),
    url(r'^(?P<q_id>[0-9]+)/primary-asset/add/$', views.primary_list_add, name='primary_list_add'),
    url(r'^(?P<q_id>[0-9]+)/primary-assets/$', views.primary_list, name='primary_list'),
    url(r'^primary-asset/(?P<primary_id>[0-9]+)/edit/$', views.primary_edit, name='primary_edit'),
    url(r'^primary-asset/(?P<primary_id>[0-9]+)/delete/$', views.primary_delete, name='primary_delete'),
    # pa of usecase process
    url(r'^(?P<u_id>[0-9]+)/primary-asset/(?P<primary_id>[0-9]+)/edit/$', views.primary_process_edit, name='primary_process_edit'),


    ## Supporting assets
    url(r'^primary-asset/(?P<pa_id>[0-9]+)/supporting-assets/add/$', views.supporting_add, name='supporting_add'),
    url(r'^primary-asset/(?P<pa_id>[0-9]+)/supporting-assets/choose$', views.supporting_choose, name='supporting_choose'),
    url(r'^primary-asset/supporting-asset/(?P<sa_id>[0-9]+)/edit/$', views.supporting_edit, name='supporting_edit'),
    url(r'^primary-asset/supporting-asset/(?P<sa_id>[0-9]+)/delete/$', views.supporting_rel_delete, name='supporting_rel_delete'),

    ## Threat Identification, Assessment
    url(r'^(?P<q_id>[0-9]+)/threat-identification/$', views.threat_identification, name='threat_identification'),
    url(r'^(?P<q_id>[0-9]+)/likelihood-assessment/$', views.threat_assessment, name='threat_assessment'),
    url(r'^(?P<q_id>[0-9]+)/threat-controls/$', views.threat_controls, name='threat_controls'),
    url(r'^(?P<sa_id>[0-9]+)/threat/add$', views.threat_sa_rel_add, name='threat_sa_rel_add'),
    url(r'^(?P<q_id>[0-9]+)/threat-rel/(?P<sa_id>[0-9]+)/threat/add$', views.threat_add, name='threat_add'),
    url(r'^(?P<q_id>[0-9]+)/threat/(?P<threat_id>[0-9]+)/delete/?$', views.threat_rel_delete, name='threat_rel_delete'),
    ## Risk Assessment
    url(r'^(?P<q_id>[0-9]+)/impact-assessment/$', views.risk_assessment, name='risk_assessment'),
    # url(r'^risk/(?P<id>[0-9]+)/edit/$', risk_edit, name='risk_edit'),
    url(r'^(?P<q_id>[0-9]+)/risk-mitigation/$', views.risk_mitigation, name='risk_mitigation'),
    ## Privacy-target identification
    url(r'^(?P<q_id>[0-9]+)/privacy-target-identification/$', views.privacy_target_identification, name='privacy_target_identification'),
    url(r'^(?P<q_id>[0-9]+)/privacy-target/(?P<target_rel_id>[0-9]+)/delete/?$', views.privacy_target_delete, name='privacy_target_delete'),
    ## Privacy-threat identification
    url(r'^(?P<q_id>[0-9]+)/privacy-threat-identification/$', views.privacy_threat_identification, name='privacy_threat_identification'),
    url(r'^(?P<q_id>[0-9]+)/privacy-threat/(?P<privacy_q_rel_id>[0-9]+)/add$', views.privacythreat_add, name='privacythreat_add'),
    url(r'^(?P<q_id>[0-9]+)/privacy-threat/(?P<privacy_threat_rel_id>[0-9]+)/primary-asset/add$', views.assign_primaryasset_to_privacythreat, name='assign_primaryasset_to_privacythreat'),
    url(r'^(?P<q_id>[0-9]+)/privacy-threat/(?P<privacy_threat_rel_id>[0-9]+)/delete$', views.privacy_threat_rel_delete, name='privacy_threat_rel_delete'),
    ## Privay control implementation
    url(r'^(?P<q_id>[0-9]+)/privacy-control-implementation/$', views.privacy_control_implementation, name='privacy_control_implementation'),
    ## Add controls to privacythreat
    url(r'^(?P<q_id>[0-9]+)/privacy-threat/(?P<privacy_threat_rel_id>[0-9]+)/privacy-control/add$', views.add_new_control_to_privacythreat, name='add_new_control_to_privacythreat'),
    url(r'^(?P<q_id>[0-9]+)/privacy-threat/(?P<privacy_threat_rel_id>[0-9]+)/privacy-controls/select$', views.add_generic_privacycontrol, name='add_generic_privacycontrol'),
    url(r'^(?P<q_id>[0-9]+)/privacy-control/(?P<threat_control_id>[0-9]+)/delete$', views.delete_selected_privacy_control, name='delete_selected_privacy_control'),

    ### VERSION CONTROL
    url(r'^deleted-questionnaires/(?P<q_id>[0-9]+)/recover/$', views.recover_questionnaire, name='recover_questionnaire'),
    url(r'^(?P<q_id>[0-9]+)/history/$', views.history, name='history'),
    url(r'^(?P<q_id>[0-9]+)/revision/(?P<revision_id>[0-9]+)/revert/$', views.revert_version, name='revert_version'),

    ### REPORTS
    url(r'^(?P<q_id>[0-9]+)/finalize-assessment/$', views.finalize_assessment, name='finalize_assessment'),
    ## Generate pdf with reportlab
    url(r'^(?P<q_id>[0-9]+)/pdf-report/$', views.pdf_reportlab, name='pdf_reportlab'),
    ## Generate word doc with python-docx
    url(r'^(?P<q_id>[0-9]+)/docx-report/$', views.generate_docx, name='generate_docx'),

    ### IMPORT-EXPORT
    url(r'^(?P<q_id>[0-9]+)/export/$', views.export_data, name="export_data"),
    url(r'^(?P<q_id>[0-9]+)/import/$', views.import_data, name="import_data"),
 ]
