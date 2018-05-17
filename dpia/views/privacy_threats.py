from dpia.modules import *

# @privacy_targets_required
@login_required
def privacy_threat_identification(request, q_id=None):
    '''
    Shows the list of all the selected privacy targets.
    The user can then assign generic privacy threats to each of the privacy targets.
    '''

    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    # query selected privacy_targets of instant q
    privacy_q_rels = PrivacyQuestionaireRel.objects.filter(questionaire=q).order_by('privacy_target')

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['privacy_q_rels'] = privacy_q_rels
    #args['privacy_threat_rels'] = privacy_threat_rels
    #args['selected_threats'] = selected_threats
    return render(request, "privacy_threats/privacy_threat_identification.html", args)


@login_required
def privacythreat_add(request, q_id=None, privacy_q_rel_id=None):
    '''
    Adds a generic threat to a privacy target.
    '''
    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    privacy_q_rel = get_object_or_404(PrivacyQuestionaireRel, questionaire=q, id=privacy_q_rel_id)
    privacy_target = get_object_or_404(PrivacyTarget, id=privacy_q_rel.privacy_target_id)

    data = dict()
    
    # Add PrivacyThreats to a PrivacyTarget
    if request.POST and request.is_ajax():
        with reversion.create_revision():
            if 'threat' in request.POST:
                checked_threats = request.POST.getlist('threat')
                pthreat_list = []
                for checked_threat in checked_threats:
                    # get the threat-object from the selected chekboxes in the template
                    threat_object = get_object_or_404(PrivacyThreat, id=checked_threat)
                    # create a new relationship with the above objects, no duplicates
                    rel, created = PrivacyThreatRel.objects.select_related('privacy_threat', 'privacy_q_rel').get_or_create(privacy_threat=threat_object, privacy_q_rel=privacy_q_rel)
                    pthreat_list.append(threat_object.name)
                # Store some meta-information.
                comment = ", ".join(pthreat_list)
                save_revision_meta(user, q, 'Added threats "{}" to privacy target "{}".'.format(comment, privacy_target))
                ## ajax data
                django_messages = []
                messages.success(request, u'Privacy threats were added successfully.')
                for message in messages.get_messages(request):
                    django_messages.append({
                        "level": message.level,
                        "message": message.message,
                        "extra_tags": message.tags,
                    })
                data['messages'] = django_messages
                data['form_is_valid'] = True
                # query selected privacy_targets of instant q
                privacy_q_rels = PrivacyQuestionaireRel.objects.filter(questionaire=q).order_by('privacy_target')
                #.prefetch_related('privacy_target', 'privacy_threats', 'privacy_q_rel__privacy_threat', 'privacy_q_rel__affected_primary_assets')\

                args = {}
                args['q'] = q
                args['privacy_q_rels'] = privacy_q_rels
                data['html_q_list'] = render_to_string('privacy_threats/partial_privacy_threats_list.html', args)
            else:
                data['form_is_valid'] = False

    # query the privacythreats the user has selected // of the instant questionaire
    #selected_threats = PrivacyThreatRel.objects.select_related('privacy_threat', 'privacy_q_rel', 'affected_primary_assets').filter(privacy_q_rel__questionaire=q)

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['privacy_q_rel'] = privacy_q_rel
    args['privacy_target'] = privacy_target
    data['html_form'] = render_to_string('privacy_threats/privacythreat_add.html', args, request=request)
    return JsonResponse(data)



@login_required
def privacy_threat_rel_delete(request, q_id=None, privacy_threat_rel_id=None):
    '''
    Removes a privacy threat from a privacy target.
    It is important to note that it doesn't delete the threat completely, since the latter is a generic one; it simply removes it from the assigned privacy target.
    '''
    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    privacy_threat_rel = get_object_or_404(PrivacyThreatRel, privacy_q_rel__questionaire=q, id=privacy_threat_rel_id)

    data = dict()

    if request.POST and request.is_ajax():
        privacy_threat_rel.delete()
        ## ajax data
        django_messages = []
        messages.success(request, u'Privacy threat "%s" was removed successfully.' %(privacy_threat_rel.privacy_threat))
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
        data['html_q_list'] = render_to_string('privacy_threats/partial_privacy_threats_list.html', args)
    else:
        args = {}
        args.update(csrf(request))
        args['q'] = q
        args['privacy_threat_rel'] = privacy_threat_rel
        data['html_form'] = render_to_string('privacy_threats/privacy_threat_remove.html', args, request=request)
    return JsonResponse(data)


@login_required
def assign_primaryasset_to_privacythreat(request, q_id=None, privacy_threat_rel_id=None):
    '''
    Adds primary assets (shows a list of all the primary assets defined in the steps before) to a privacy threat.
    '''

    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    privacy_threat_rel = get_object_or_404(PrivacyThreatRel, privacy_q_rel__questionaire=q, id=privacy_threat_rel_id)
    # query all the primaries of the q for the queryset of the formset
    primaries = Primary.objects.all().filter(questionaire=q)
    # query only the privacy-threats of the instant privacy-threat-rel
    privacy_threat = PrivacyThreatRel.objects.filter(id=privacy_threat_rel_id)
    ## PrimaryAssetsFormset
    addPAFormset = modelformset_factory(PrivacyThreatRel, form=PrivacyThreatRelForm, fields=('affected_primary_assets',), can_delete=False, extra=0)
    data = dict()
    # Formset
    if request.POST and request.is_ajax():
        add_pa_formset = addPAFormset(request.POST, request.FILES)
        for form in add_pa_formset.forms:
            form.fields['affected_primary_assets'].queryset = primaries
        if add_pa_formset.is_valid():
            with reversion.create_revision():
                add_pa_formset.save()
                # Store some meta-information.
                save_revision_meta(user, q, 'Assigned primary asset(s) to privacy threat "%s".' %(privacy_threat_rel.privacy_threat))
                ## ajax data
                django_messages = []
                messages.success(request, u'Primary assets were submitted successfully to privacy threat "%s".' %(privacy_threat_rel.privacy_threat))
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
                data['html_q_list'] = render_to_string('privacy_threats/partial_privacy_threats_list.html', args)
        else:
            data['form_is_valid'] = False
    else:
        add_pa_formset = addPAFormset(queryset=privacy_threat)
        for form in add_pa_formset.forms:
            form.fields['affected_primary_assets'].queryset = primaries
            form.empty_permitted = False

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['privacy_threat'] = privacy_threat
    args['privacy_threat_rel'] = privacy_threat_rel
    args['add_pa_formset'] = add_pa_formset
    data['html_form'] = render_to_string('privacy_threats/privacythreat_primaryasset_add.html', args, request=request)
    return JsonResponse(data)
