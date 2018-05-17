from dpia.modules import *


@login_required
@q_pa_sa_lookup
def threat_identification(request, q_id=None):
    '''
    Shows a list of the added supporting assets which are assigned to a primary asset.
    The user here selects threats from the list of generic threats or adds a new threat to a supporting asset.
    '''
    queryuser = UserProfile.objects.all().filter(user=request.user)
    q = get_object_or_404(Questionaire, membership__member=queryuser, id=q_id)
    # query supporting assets
    supporting_assets = Supporting.objects.select_related('questionaire').prefetch_related('affected_supporting', 'affected_supporting__threat').filter(supporting__primary__questionaire=q).distinct()


    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['queryuser'] = queryuser
    args['supporting_assets'] = supporting_assets
    return render(request, "threats/threat_identification.html", args)


# supporting-asset add
@login_required
def threat_sa_rel_add(request, sa_id=None):
    '''
    Adds generic threats to a supporting asset.
    '''

    queryuser = UserProfile.objects.all().filter(user=request.user)
    supporting_object = get_object_or_404(Supporting, id=sa_id)
    if supporting_object:
        pa_sa_rel = PrimarySupportingRel.objects.all().filter(supporting = supporting_object)[0] #[0] to select only one object when there are duplicates
    primary_id = pa_sa_rel.primary_id
    primary = get_object_or_404(Primary, id=primary_id)
    q = get_object_or_404(Questionaire, membership__member=queryuser, id=primary.questionaire_id)

    data = dict()
    ## Add Threats to a SA
    with reversion.create_revision():
        if request.POST and request.is_ajax():
            if 'threat' in request.POST:
                checked_threats = request.POST.getlist('threat')
                for checked_threat in checked_threats:
                    threat_object = get_object_or_404(Threat, id=checked_threat)
                    # create a new relationship with the above objects, no duplicates
                    rel, created = Threat_SA_REL.objects.get_or_create(affected_supporting_asset = supporting_object, threat = threat_object)

                # Store some meta-information.
                reversion.set_user(request.user)
                reversion.set_comment('Added generic threats to supporting asset "%s".' %(supporting_object))
                membership = get_object_or_404(Membership, questionaire=q, owner=True)
                owner = membership.member.user.username
                reversion.add_meta(VersionOwner, owner=owner)
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

                if q.step_threat_id == 0:
                    q.step_threat_id = 5
                    q.step_total = q.step_total + 5
                else:
                    q.step_threat_id = 5
                    q.step_total = q.step_total
                q.save()
                data['q_total'] = q.step_total

                # query supporting assets
                supporting_assets = Supporting.objects.select_related('questionaire').prefetch_related('affected_supporting', 'affected_supporting__threat').filter(supporting__primary__questionaire=q).distinct()
                args = {}
                args['supporting_assets'] = supporting_assets
                args['q'] = q
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
    queryuser = UserProfile.objects.all().filter(user=request.user)
    q = get_object_or_404(Questionaire, membership__member=queryuser, id=q_id)
    sa = get_object_or_404(Supporting, id=sa_id)

    data = dict()
    ## Add Threat
    with reversion.create_revision():
        threat_form = ThreatForm()
        if request.POST and request.is_ajax():
            threat_form = ThreatForm(request.POST)
            if threat_form.is_valid():
                threat = threat_form.save(commit=False)
                threat.supporting_asset_type = sa.supporting_type
                threat.save()
                new_threat_sa_rel = Threat_SA_REL.objects.get_or_create(affected_supporting_asset = sa, threat = threat)

                # Store some meta-information.
                reversion.set_user(request.user)
                reversion.set_comment('Added new threat "%s" to supporting asset "%s".' %(threat.name, sa))
                membership = get_object_or_404(Membership, questionaire=q, owner=True)
                owner = membership.member.user.username
                reversion.add_meta(VersionOwner, owner=owner)
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

                if q.step_threat_id == 0:
                    q.step_threat_id = 5
                    q.step_total = q.step_total + 5
                else:
                    q.step_threat_id = 5
                    q.step_total = q.step_total
                q.save()
                data['q_total'] = q.step_total

                # query supporting assets
                supporting_assets = Supporting.objects.select_related('questionaire').prefetch_related('affected_supporting', 'affected_supporting__threat').filter(supporting__primary__questionaire=q).distinct()
                args = {}
                args['supporting_assets'] = supporting_assets
                args['q'] = q
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
    queryuser = get_object_or_404(UserProfile, user=request.user)
    q = get_object_or_404(Questionaire, membership__member=queryuser, id=q_id)
    threat_rel = get_object_or_404(Threat_SA_REL, id=threat_id)

    data = dict()

    with reversion.create_revision():
        if request.POST and request.is_ajax():
            threat_rel.delete()
            # Store some meta-information.
            reversion.set_user(request.user)
            reversion.set_comment('Removed threat "%s" from "%s".' %(threat_rel.threat, threat_rel.affected_supporting_asset))
            membership = get_object_or_404(Membership, questionaire=q, owner=True)
            owner = membership.member.user.username
            reversion.add_meta(VersionOwner, owner=owner)
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
            selected_threats = Threat_SA_REL.objects.select_related('affected_supporting_asset', 'threat').filter(affected_supporting_asset__questionaire = q)
            if not selected_threats.exists():
                q.step_threat_id = 0
                q.step_total = q.step_total - 5
                q.save()
            data['q_total'] = q.step_total

            # query supporting assets
            supporting_assets = Supporting.objects.select_related('questionaire').prefetch_related('affected_supporting', 'affected_supporting__threat').filter(supporting__primary__questionaire=q).distinct()
            args = {}
            args['supporting_assets'] = supporting_assets
            args['q'] = q
            data['html_q_list'] = render_to_string('threats/partial_threats_list.html', args)
        else:
            args = {}
            args.update(csrf(request))
            args['q'] = q
            args['threat_rel'] = threat_rel
            data['html_form'] = render_to_string('threats/threat_rel_remove.html', args, request=request)
        return JsonResponse(data)


@login_required
@q_threat_id_lookup
def threat_assessment(request, q_id=None):
    '''
    Shows a formset table of all the threats (ordered by their "likelihood" value) selected by the user in the step "Threat Identification".
    It accepts two values, namely "level of vulnerability" and "risk source capability".
    If either of them is entered above the max number value (4) or not entered at all, an error is raised.
    The likelihood value is automatically calculated as the sum of the level of vulnerability and risk source capability.
    '''

    queryuser = UserProfile.objects.all().filter(user=request.user)
    q = get_object_or_404(Questionaire, membership__member=queryuser, id=q_id)
    # query threats the user has selected and order by the MaxValue of the Sum
    selected_threats = Threat_SA_REL.objects.select_related('affected_supporting_asset', 'threat').select_for_update(nowait=False).filter(affected_supporting_asset__questionaire = q).order_by('-likelihood')
    ## Assess Threats
    ThreatFormset = modelformset_factory(Threat_SA_REL, form=Threat_SA_REL_Form, extra=0)
    threat_formset = ThreatFormset(queryset=selected_threats)

    data = dict()

    threat_form = ThreatAssessmentForm(request.POST or None)
    with reversion.create_revision():
        if request.POST:
            if threat_form.is_valid():
                selected_option = request.POST.get('level_of_vulnerability', None)
                threat_id = request.POST.get('threat_id', None)
                threat_sa_rel = get_object_or_404(Threat_SA_REL, id=threat_id)
                threat_sa_rel.level_of_vulnerability = selected_option
                threat_sa_rel.save()

                if q.step_likelihood == 0:
                    q.step_likelihood = 5
                    q.step_total = q.step_total + 5
                else:
                    q.step_total = q.step_total
                q.save()

                # Store some meta-information.
                reversion.set_user(request.user)
                reversion.set_comment("Assessed likelihood of threats.")
                membership = get_object_or_404(Membership, questionaire=q, owner=True)
                owner = membership.member.user.username
                reversion.add_meta(VersionOwner, owner=owner)

                ## ajax data
                django_messages = []
                messages.success(request, u'Threats were assessed successfully.')
                for message in messages.get_messages(request):
                    django_messages.append({
                        "level": message.level,
                        "message": message.message,
                        "extra_tags": message.tags,
                    })
                data['form_is_valid'] = True
                data['messages'] = django_messages
                data['q_total'] = q.step_total
                #query the saved sources
                args = {}
                args['q'] = q
                args['selected_threats'] = selected_threats
                data['html_q_list'] = render_to_string('threats/partial_threat_assessment_list.html', args, request=request)

            else:
                data['form_is_valid'] = False


    ## To activate the Next Step
    step_threats = Threat_SA_REL.objects.all().filter(affected_supporting_asset__primary__questionaire_id=q, level_of_vulnerability__isnull=False, risk_source_capability__isnull=False)
    if not step_threats:
        q.step_likelihood=0
        q.save()


    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['selected_threats'] = selected_threats
    args['step_threats'] = step_threats
    args['threat_form'] = threat_form
    return render(request, "threats/threat_assessment.html", args)

    # data['html_form'] = render_to_string('threats/threat_assessment.html', args, request=request)
    # return JsonResponse(data)


@login_required
@q_impact_lookup
def threat_controls(request, q_id=None):
    '''
    Shows a formset list of all the assessed threats.
    The user is required to fill out only the controls field.
    '''

    queryuser = UserProfile.objects.all().filter(user=request.user)
    q = get_object_or_404(Questionaire, membership__member=queryuser, id=q_id)

    ## query Threats
    threats = Threat_SA_REL.objects.select_related('affected_supporting_asset', 'threat').prefetch_related('threat').filter(affected_supporting_asset__questionaire=q).order_by('-likelihood')
    ThreatFormset2 = modelformset_factory(Threat_SA_REL, form=Threat_SA_REL_Form2, extra=0)

    with reversion.create_revision():
        if request.POST:
            threat_formset = ThreatFormset2(request.POST, queryset=threats)
            for form in threat_formset.forms:
                form.fields['control'].required = True
            if threat_formset.is_valid():
                threat_formset.save()
                if q.step_control == 0:
                    q.step_control = 10
                    q.step_total = q.step_total + 10
                else:
                    q.step_total = q.step_total
                q.save()

                # Store some meta-information.
                reversion.set_user(request.user)
                reversion.set_comment("Implemented threat controls.")
                membership = get_object_or_404(Membership, questionaire=q, owner=True)
                owner = membership.member.user.username
                reversion.add_meta(VersionOwner, owner=owner)
                # update_q = Questionaire.objects.all().filter(id=q_id).update(step_control=10)
                messages.success(request, u'Controls were implemented successfully.')
                return HttpResponseRedirect(reverse_lazy('risk_mitigation', args=[q.id]))
            else:
                # pass
                messages.error(request, u'Please fill out the required fields.')
        else:
            threat_formset = ThreatFormset2(queryset=threats)


    ## To activate the Next Step
    step_threat_controls = Threat_SA_REL.objects.all().filter(affected_supporting_asset__primary__questionaire_id=q, control__isnull=False)

    if not step_threat_controls:
        q.step_control=0
        q.save()

    ### Calculate the risk level of the risks
    ## query Risks
    risks = Risk.objects.select_related('primary_asset_affected', 'risk_owner').prefetch_related('risk_owner', 'primary_asset_affected__primary_supporting', 'primary_asset_affected__primary_supporting__supporting', 'primary_asset_affected__primary_supporting__supporting__affected_supporting', 'primary_asset_affected__primary_supporting__supporting__affected_supporting__threat').filter(primary_asset_affected__questionaire=q).order_by('-impact')


    if risks:
        for risk in risks:
            # get the max likelihood of threats related to this risks
            max_likelihood = Threat_SA_REL.objects.select_related('affected_supporting_asset', 'threat').prefetch_related('threat', 'affected_supporting_asset__primary',  'affected_supporting_asset__primary__primary_affected').filter(affected_supporting_asset__primary__primary_affected__type_of_jeopardy=risk.type_of_jeopardy, affected_supporting_asset__primary=risk.primary_asset_affected).aggregate(max_likelihood_alias=Max('likelihood')).values()[0]

            risk.risk_level = max_likelihood + risk.impact
            risk.max_likelihood = max_likelihood
            risk.save()


    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['threat_formset'] = threat_formset
    return render(request, "threats/threat_controls.html", args)
