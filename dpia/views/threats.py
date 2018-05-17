from dpia.modules import *

# @primary_assets_required
# @supporting_assets_required
@login_required
def threat_identification(request, q_id=None):
    '''
    Shows a list of the added supporting assets which are assigned to a primary asset.
    The user here selects threats from the list of generic threats or adds a new threat to a supporting asset.
    '''
    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    # query supporting assets
    supporting_assets = Supporting.objects.filter(supporting_in_psrel__primary__questionaire=q).distinct()

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['supporting_assets'] = supporting_assets
    return render(request, "threats/threat_identification.html", args)


# supporting-asset add
@login_required
def threat_sa_rel_add(request, sa_id=None):
    '''
    Adds generic threats to a supporting asset.
    '''
    user = request.user
    supporting_object = get_object_or_404(Supporting, id=sa_id)
    if supporting_object:
        pa_sa_rel = PrimarySupportingRel.objects.filter(supporting=supporting_object)[0] # [0]: to select only one object when there are duplicates
    primary_id = pa_sa_rel.primary_id
    primary = get_object_or_404(Primary, id=primary_id)
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=primary.questionaire_id)

    data = dict()
    ## Add Threats to a SA

    if request.POST and request.is_ajax():
        if 'threat' in request.POST:
            with reversion.create_revision():
                checked_threats = request.POST.getlist('threat')
                threat_list = []
                for checked_threat in checked_threats:
                    threat_object = get_object_or_404(Threat, id=checked_threat)
                    # create a new relationship with the above objects, no duplicates
                    rel, created = Threat_SA_REL.objects.get_or_create(affected_supporting_asset=supporting_object, threat=threat_object)
                    threat_list.append(threat_object.name)
                comment = ", ".join(threat_list)
                # Store some meta-information.
                save_revision_meta(user, q, 'Added generic threats "%s" to supporting asset "%s".' %(comment, supporting_object))
                ## ajax data
                django_messages = []
                messages.success(request, u'Generic threats were added successfully to supporting asset "%s".' %(supporting_object))
                for message in messages.get_messages(request):
                    django_messages.append({
                        "level": message.level,
                        "message": message.message,
                        "extra_tags": message.tags,
                    })
                data['messages'] = django_messages
                data['form_is_valid'] = True

                # query supporting assets
                supporting_assets = Supporting.objects.filter(supporting_in_psrel__primary__questionaire=q).distinct()
                args = {}
                args['q'] = q
                args['supporting_assets'] = supporting_assets
                data['html_q_list'] = render_to_string('threats/partial_threats_list.html', args)
        else:
            data['form_is_valid'] = False


    # query generic_threats and each newly created Threat per questionnaire
    generic_threats = Threat.objects.all() #.exclude(~Q(threat_sa_rel__affected_supporting_asset__primary__questionaire=q), threat_sa_rel__affected_supporting_asset__primary__questionaire__isnull=False).order_by("type_of_jeopardy")
    # # query threats the user selects // of the instant questionaire
    # selected_threats = Threat_SA_REL.objects.prefetch_related().all().filter(affected_supporting_asset__primary__questionaire=q).distinct()

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['supporting_object'] = supporting_object
    args['generic_threats'] = generic_threats
    args['primary'] = primary
    data['html_form'] = render_to_string('threats/threat_sa_rel_add.html', args, request=request)
    return JsonResponse(data)



@login_required
def threat_add(request, q_id=None, sa_id=None):
    '''
    Adds new threats (defined by the user) to a supporting asset.
    '''
    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    sa = get_object_or_404(Supporting, id=sa_id)

    data = dict()
    ## Add Threat
    threat_form = ThreatForm(request.POST or None)
    if request.POST and request.is_ajax():
        if threat_form.is_valid():
            with reversion.create_revision():
                threat = threat_form.save(commit=False)
                threat.supporting_asset_type = sa.supporting_type
                threat.save()
                new_threat_sa_rel = Threat_SA_REL.objects.get_or_create(affected_supporting_asset=sa, threat=threat)
                # Store some meta-information.
                save_revision_meta(user, q, 'Added new threat "%s" to supporting asset "%s".' %(threat.name, sa))
                ## ajax data
                django_messages = []
                messages.success(request, u'New threat "%s" was added successfully to supporting asset "%s".' %(threat.name, sa))
                for message in messages.get_messages(request):
                    django_messages.append({
                        "level": message.level,
                        "message": message.message,
                        "extra_tags": message.tags,
                    })
                data['messages'] = django_messages
                data['form_is_valid'] = True

                # query supporting assets
                supporting_assets = Supporting.objects.filter(supporting_in_psrel__primary__questionaire=q).distinct()
                args = {}
                args['q'] = q
                args['supporting_assets'] = supporting_assets
                data['html_q_list'] = render_to_string('threats/partial_threats_list.html', args)
        else:
            data['form_is_valid'] = False


    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['sa'] = sa
    args['threat_form'] = threat_form
    data['html_form'] = render_to_string('threats/threat_add.html', args, request=request)
    return JsonResponse(data)


@login_required
def threat_rel_delete(request, q_id=None, threat_id=None):
    '''
    Delete a relationship between threat and supporting asset.
    It doesn't delete the threat completely; it simply removes it from the supporting asset it is assigned to.
    '''
    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    threat_rel = get_object_or_404(Threat_SA_REL, id=threat_id)

    data = dict()

    if request.POST and request.is_ajax():
        threat_rel.delete()
        ## ajax data
        django_messages = []
        messages.success(request, u'Threat "%s" was removed successfully from supporting asset "%s".' %(threat_rel.threat, threat_rel.affected_supporting_asset))
        for message in messages.get_messages(request):
            django_messages.append({
                "level": message.level,
                "message": message.message,
                "extra_tags": message.tags,
            })
        data['form_is_valid'] = True
        data['messages'] = django_messages
        # query threats the user has selected and order by the MaxValue of the Sum
        selected_threats = Threat_SA_REL.objects.filter(affected_supporting_asset__questionaire=q)
        # query supporting assets
        supporting_assets = Supporting.objects.filter(supporting_in_psrel__primary__questionaire=q).distinct()
        args = {}
        args['q'] = q
        args['supporting_assets'] = supporting_assets
        data['html_q_list'] = render_to_string('threats/partial_threats_list.html', args)
    else:
        args = {}
        args.update(csrf(request))
        args['q'] = q
        args['threat_rel'] = threat_rel
        data['html_form'] = render_to_string('threats/threat_rel_remove.html', args, request=request)
    return JsonResponse(data)


# @supporting_assets_required
# @threats_required
@login_required
def threat_assessment(request, q_id=None):
    '''
    Shows a formset table of all the threats (ordered by their "likelihood" value) selected by the user in the step "Threat Identification".
    It accepts two values, namely "level of vulnerability" and "risk source capability".
    If either of them is entered above the max number value (4) or not entered at all, an error is raised.
    The likelihood value is automatically calculated as the sum of the level of vulnerability and risk source capability.
    '''

    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    # query threats the user has selected and order by the MaxValue of the Sum;
    # and filter only those that have a relationship to a primary asset. the "is_null" filtering is done in case the user goes back to
    # the primary list step to remove supporting assets.
    selected_threats = q.get_threats()
    ## Selected threats formset
    ThreatFormset = modelformset_factory(Threat_SA_REL, form=Threat_SA_REL_Form, extra=0)
    threat_formset = ThreatFormset(queryset=selected_threats)
    if request.POST:
        if selected_threats.exists():
            threat_formset = ThreatFormset(request.POST, request.FILES)
            if threat_formset.is_valid():
                with reversion.create_revision():
                    for form in threat_formset.forms:
                        threat = form.save(commit=False)
                        threat.likelihood = threat.level_of_vulnerability + threat.risk_source_capability
                        threat.save()
                    threat_formset.save()
                    threat_list = selected_threats.values_list('threat__name', flat=True)
                    comment = ", ".join(threat_list)
                    # Store some meta-information.
                    save_revision_meta(user, q, 'Assessed likelihood of threats "{}".'.format(comment))
                    messages.success(request, u'Likelihood of threats was assessed successfully.')
                    return redirect(reverse('risk_assessment', args=[q.id]))
            else:
                messages.error(request, u'Please fill out the required fields.')
        else:
            return redirect('risk_assessment', q.id)

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['selected_threats'] = selected_threats
    args['threat_formset'] = threat_formset
    return render(request, "threats/threat_assessment.html", args)



# @supporting_assets_required
# @threats_required
# @threat_assessment_required
# @risk_assessment_required
@login_required
def threat_controls(request, q_id=None):
    '''
    Shows a formset list of all the assessed threats.
    The user is required to fill out only the controls field.
    '''
    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    ## query Threats
    threats = q.get_threats()

    ThreatFormset2 = modelformset_factory(Threat_SA_REL, form=Threat_SA_REL_Form2, extra=0)

    if request.POST:
        if threats.exists():
            threat_formset = ThreatFormset2(request.POST, queryset=threats)
            for form in threat_formset.forms:
                form.fields['control'].required = True
            with reversion.create_revision():
                if threat_formset.is_valid():
                    threat_formset.save()
                    # Store some meta-information.
                    threat_list = threats.values_list('threat__name', flat=True)
                    comment = ", ".join(threat_list)
                    save_revision_meta(user, q, 'Implemented controls to threats "{}".'.format(comment))
                    messages.success(request, u'Controls were implemented successfully.')
                    return redirect(reverse('risk_mitigation', args=[q.id]))
                else:
                    messages.error(request, u'Please fill out the required fields.')
        else:
            return redirect('risk_mitigation', q.id)
    else:
        threat_formset = ThreatFormset2(queryset=threats)

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['threat_formset'] = threat_formset
    return render(request, "threats/threat_controls.html", args)
