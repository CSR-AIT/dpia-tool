from dpia.modules import *


# @primary_assets_required
# @supporting_assets_required
# @threats_required
# @threat_assessment_required
@login_required
def risk_assessment(request, q_id=None):
    '''
    Creates risk objects based on the primary assets that are affected and the type of jeopardy the threats of the supporting assets which are related to these primary assets.
    It then lists these risk objects, showing only the name of the primary assets and the type of jeopardy, and the other fields are empty for the user to fill out (consequences, risk owner, prejudicial_effects).
    The impact value is automatically calculated as the sum of level of identification of the primary asset affected and the prejudicial effects of the risk.
    '''
    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    ## query all primary assets of the instant questionnaire
    primaries = Primary.objects.filter(questionaire=q)
    # show all the generic actors and the the actors created in the instant questionaire
    actors = Actor.objects.select_related('usecase').exclude(~Q(usecase__questionaire=q), usecase__questionaire__isnull=False)
    ## query all primary assets of the instant questionnaire
    primary_rels = PrimarySupportingRel.objects\
        .select_related('primary', 'supporting').filter(primary__questionaire=q, supporting__supporting_in_threatsarel__isnull=False).distinct()
    ## get only the threat-rels that are assessed to create the risks based on their identification
    threats = Threat_SA_REL.objects\
        .filter(affected_supporting_asset__supporting_in_psrel__primary__questionaire=q, threat__isnull=False, affected_supporting_asset__supporting_in_psrel__isnull=False,
        affected_supporting_asset__isnull=False, level_of_vulnerability__isnull=False, risk_source_capability__isnull=False)\
        .distinct()

    ## query risks
    risks = q.get_risks().distinct()

    # Create Risk Objects for every Primary Objects
    if primary_rels and threats:
        for threatrel in threats:
            for primary_rel in primary_rels:
                if threatrel.affected_supporting_asset == primary_rel.supporting:
                    risk_object = Risk.objects\
                    .get_or_create(primary_asset_affected=primary_rel.primary, type_of_jeopardy=threatrel.threat.type_of_jeopardy)


    ## assess risks
    RiskFormset = modelformset_factory(Risk, form=RiskForm, extra=0) # RiskFormset
    risk_formset = RiskFormset(request.POST or None, queryset=risks)
    for form in risk_formset.forms:
        form.fields['risk_owner'].queryset = actors
    if request.POST:
        if risks.exists():
            for form in risk_formset.forms:
                form.fields['risk_owner'].queryset = actors
            if risk_formset.is_valid():
                with reversion.create_revision():
                    for form in risk_formset.forms:
                        risk = form.save(commit=False)
                        risk.impact = risk.prejudicial_effects + risk.primary_asset_affected.level_of_identification
                        risk.save()
                    risk_formset.save()
                    # Store meta-information.
                    save_revision_meta(user, q, 'Assessed impact values of {} risks'.format(risks.count()))
                    # update_q = Questionaire.objects.all().filter(id=q_id).update(step_impact=10) # update Questionaire Step
                    messages.success(request, u'Impact of risks was assessed successfully.')
                    return redirect(reverse('threat_controls', args=[q.id]))
            else:
                messages.error(request, u'Please fill out the required fields.')
        else:
            return redirect('threat_controls', q.id)
    else:
        for form in risk_formset.forms:
            form.fields['risk_owner'].queryset = actors

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['primaries'] = primaries
    args['risks'] = risks
    args['risk_formset'] = risk_formset
    return render(request, "risks/risk_assessment.html", args)





# @primary_assets_required
# @supporting_assets_required
# @threats_required
# @threat_assessment_required
# @risk_assessment_required
# @threat_controls_required
@login_required
def risk_mitigation(request, q_id=None):
    '''
    Shows a formset list of all the risks, together with their associated threats.
    The user is required to fill out the risk treatment and the residual risk of each risk.
    Here the maximum likelihood of the threats is calculated as well.
    '''
    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    risks = q.get_risks()

    calc_risks = Risk.objects.filter(primary_asset_affected__questionaire=q,
                primary_asset_affected__level_of_identification__isnull=False,
                consequences__isnull=False,
                prejudicial_effects__isnull=False) \
                .order_by('-impact')
    if calc_risks:
        for risk in calc_risks:
            risk.impact = risk.prejudicial_effects + risk.primary_asset_affected.level_of_identification
            # get the max likelihood of threats related to this risk
            max_likelihood = Threat_SA_REL.objects.filter(affected_supporting_asset__supporting_in_psrel__primary__questionaire=q,
                affected_supporting_asset__isnull=False,
                affected_supporting_asset__supporting_in_threatsarel__threat__type_of_jeopardy=risk.type_of_jeopardy,
                affected_supporting_asset__primary=risk.primary_asset_affected)\
                .aggregate(max_likelihood_alias=Max('likelihood')).values()[0]
            max_l = 0
            if max_likelihood is not None:
                max_l = max_likelihood
            risk.max_likelihood = max_l
            risk.risk_level = max_l + risk.impact
            risk.save()

    RiskFormset = modelformset_factory(Risk, form=RiskForm2, extra=0)
    if request.POST:
        if risks.exists():
            risk_formset = RiskFormset(request.POST, queryset=risks)
            for form in risk_formset.forms:
                form.fields['risk_treatment'].required = True
                form.fields['residual_risk'].required = True
            if risk_formset.is_valid():
                with reversion.create_revision():
                    risk_formset.save()
                    # Store some meta-information.
                    save_revision_meta(user, q, "Assigned treatment and residual values to {} risks.".format(risks.count()))
                    messages.success(request, u'Risks were mitigated successfully.')
                    return redirect(reverse('privacy_target_identification', args=[q.id]))
            else:
                messages.error(request, u'Please fill out the required fields.')
        else:
            return redirect('privacy_target_identification', q.id)
    else:
        risk_formset = RiskFormset(queryset=risks)

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['risks'] = risks
    args['risk_formset'] = risk_formset
    return render(request, "risks/risk_mitigation.html", args)
