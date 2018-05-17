from dpia.modules import *


# @privacy_targets_required
# @privacy_threats_required
@login_required
def privacy_control_implementation(request, q_id=None):
    '''
    Shows the list of the identified privacy threats (related to privacy targets).
    '''
    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    # query privacy_targets of instant q
    privacy_q_rels = PrivacyQuestionaireRel.objects.filter(questionaire=q).order_by('privacy_target')

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['privacy_q_rels'] = privacy_q_rels
    return render(request, "privacy_controls/privacy_control_implementation.html", args)



@login_required
def add_generic_privacycontrol(request, q_id=None, privacy_threat_rel_id=None):
    '''
    Adds generic privacy controls to a privacy threat (which is related to a privacy target).
    '''
    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    privacy_threat_rel = get_object_or_404(PrivacyThreatRel, id=privacy_threat_rel_id)
    # query only the privacy-threat of the instant privacy-threat-rel
    privacy_threat = get_object_or_404(PrivacyThreat, id=privacy_threat_rel.privacy_threat_id)

    data = dict()
    # Add PrivacyThreats to a PrivacyTarget
    if request.POST and request.is_ajax():
        if 'control' in request.POST:
            with reversion.create_revision():
                checked_controls = request.POST.getlist('control')
                pcontrol_list = []
                for checked_control in checked_controls:
                    # get the control-object from the selected chekboxes in the template
                    control_object = get_object_or_404(PrivacyControl, id=checked_control)
                    # create a new relationship with the above objects, no duplicates
                    rel, created = PrivacyThreatControl.objects.get_or_create(privacy_threat_rel=privacy_threat_rel, privacy_control=control_object)
                    pcontrol_list.append(control_object.name)
                # Store some meta-information.
                comment = ", ".join(pcontrol_list)
                save_revision_meta(user, q,'Added privacy controls "{}" to privacy threat "{}".'.format(comment, privacy_threat))
                ## ajax data
                django_messages = []
                messages.success(request, u'Privacy controls were added successfully to privacy threat "%s".' %(privacy_threat))
                for message in messages.get_messages(request):
                    django_messages.append({
                        "level": message.level,
                        "message": message.message,
                        "extra_tags": message.tags,
                    })
                data['form_is_valid'] = True
                data['messages'] = django_messages
                # query privacy_targets of instant q
                privacy_q_rels = PrivacyQuestionaireRel.objects.filter(questionaire=q).order_by('privacy_target')
                args = {}
                args['q'] = q
                args['privacy_q_rels'] = privacy_q_rels
                data['html_q_list'] = render_to_string('privacy_controls/partial_privacy_controls_list.html', args)
        else:
            data['form_is_valid'] = False

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['privacy_threat_rel'] = privacy_threat_rel
    args['privacy_threat'] = privacy_threat
    data['html_form'] = render_to_string('privacy_controls/privacy_control_select.html', args, request=request)
    return JsonResponse(data)


@login_required
def delete_selected_privacy_control(request, q_id=None, threat_control_id=None):
    '''
    Removes a privacy control from a privacy threat.
    '''
    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    threat_control = get_object_or_404(PrivacyThreatControl, id=threat_control_id)
    data = dict()

    if request.POST and request.is_ajax():
        with reversion.create_revision():
            threat_control.delete()
            # Store some meta-information.
            save_revision_meta(user, q, "Removed privacy control.")
            ## ajax data
            django_messages = []
            messages.success(request, u'Privacy control was removed successfully from privacy threat "%s".' %(threat_control.privacy_threat_rel.privacy_threat))
            for message in messages.get_messages(request):
                django_messages.append({
                    "level": message.level,
                    "message": message.message,
                    "extra_tags": message.tags,
                })
            data['form_is_valid'] = True
            data['messages'] = django_messages
            # query selected privacy_targets of instant q
            privacy_q_rels = PrivacyQuestionaireRel.objects.filter(questionaire=q).order_by('privacy_target')
            args = {}
            args['q'] = q
            args['privacy_q_rels'] = privacy_q_rels
            data['html_q_list'] = render_to_string('privacy_controls/partial_privacy_controls_list.html', args)
    else:
        args = {}
        args.update(csrf(request))
        args['q'] = q
        args['threat_control'] = threat_control
        data['html_form'] = render_to_string('privacy_controls/privacy_control_remove.html', args, request=request)
    return JsonResponse(data)




@login_required
def add_new_control_to_privacythreat(request, q_id=None, privacy_threat_rel_id=None):
    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    privacy_threat_rel = get_object_or_404(PrivacyThreatRel, id=privacy_threat_rel_id)
    # query only the privacy-threats of the instant privacy-threat-rel
    privacy_threat = get_object_or_404(PrivacyThreat, id=privacy_threat_rel.privacy_threat_id)
    ## Add new Control
    with reversion.create_revision():
        if request.POST:
            control_form = PrivacyControlForm(request.POST)
            if control_form.is_valid():
                control = control_form.save(commit=False)
                control.save()
                privacy_threat.privacy_controls.add(control)
                save_revision_meta(user, q, "Submitted primary assets to privacy control.")
                messages.success(request, u'Affected primary assets submitted successfully.')
                return redirect(reverse('privacy_control_implementation', args=[q.id]))
        else:
            control_form = PrivacyControlForm()

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['privacy_threat'] = privacy_threat
    args['privacy_threat_rel'] = privacy_threat_rel
    args['control_form'] = control_form
    return render(request, "privacy_controls/privacythreat_add_new_control.html", args)
