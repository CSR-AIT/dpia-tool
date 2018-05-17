from dpia.modules import *

### PREVIEW

# @primary_assets_required
# @supporting_assets_required
# @threats_required
# @threat_assessment_required
# @risk_assessment_required
# @threat_controls_required
# @privacy_targets_required
# @privacy_threats_required
# @privacy_controls_required
@login_required
def finalize_assessment(request, q_id=None):
    '''
    Queries everything filled out by the user, and lists them in tables.
    '''
    q = get_object_or_404(Questionaire.objects.prefetch_related('q_in_membership__member', 'q_in_membership__member__user_profile', 'q_in_source'), q_in_membership__member=request.user, id=q_id)
    # html report
    reporter = request.user
    report_time = datetime.now()

    ## recalculate the risk level of the risks
    calc_risks = Risk.objects.filter(primary_asset_affected__questionaire=q,
                # primary_asset_affected__primary_in_psrel__supporting__supporting_in_threatsarel__isnull=False,
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

    risks = q.get_risks()
    high_risks = q.get_high_risks()
    high_threats = q.get_high_threats()
    ptargets = PrivacyQuestionaireRel.objects.select_related('questionaire', 'privacy_target').prefetch_related('pqrel_in_pthreatrel__privacy_threat', 'pqrel_in_pthreatrel__controls').filter(questionaire=q)
    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['report_time'] = datetime.now()
    args['reporter'] = reporter
    args['risks'] = risks
    args['high_risks'] = high_risks
    args['high_threats'] = high_threats
    args['ptargets'] = ptargets
    return render(request, "finalize_assessment.html", args)
