from dpia.modules import *
from dpia.views.generic_dicts import ptargets_dict

@login_required
def privacy_target_identification(request, q_id=None):
    '''
    Shows a list of selectable generic privacy targets.
    The selected privacy targets by the user are listed in another list above the generic one.
    '''
    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)

    '''
        Add targets, threats and controls fron generic dicts.
    '''

    targets = PrivacyTarget.objects.all()
    if not targets.exists():
        for list in ptargets_dict.values():
            p = PrivacyTarget.objects.get_or_create(name=list[0], description=list[1])


    ## Add PrivacyTarget to a Q
    if request.POST and '_choose' in request.POST:
        if 'privacy_target' in request.POST:
            with reversion.create_revision():
                # create list of checked targets
                checked_targets_list = request.POST.getlist('privacy_target')
                ptarget_list = []
                # create new p-q-rel objects
                for checked_privacy_target in checked_targets_list:
                    # get the privacy-target-object from the selected chekboxes in the template
                    privacy_target_object = get_object_or_404(PrivacyTarget, id=checked_privacy_target)
                    # add the instant questionnaire to the privacy target
                    rel, created = PrivacyQuestionaireRel.objects.select_related('questionaire', 'privacy_target').get_or_create(questionaire=q, privacy_target=privacy_target_object)
                    ptarget_list.append(privacy_target_object.name)
                # Store some meta-information.
                comment = ", ".join(ptarget_list)
                save_revision_meta(user, q, 'Added privacy targets "{}".'.format(comment))
                # update_q = Questionaire.objects.all().filter(id=q_id).update(step_ptarget=10) # update Questionaire Step
                messages.success(request, u'Privacy targets were added successfully.')
                return redirect(reverse('privacy_threat_identification', args=[q.id]))
        else:
            return redirect('privacy_threat_identification', q.id)
            # messages.error(request, u'Please select at least one privacy target.')

    # query generic_privacy_targets
    generic_privacy_targets = PrivacyTarget.objects.all()
    # query generic_privacy_targets the user selects // of the instant questionaire
    selected_privacy_targets = PrivacyQuestionaireRel.objects.select_related('questionaire', 'privacy_target').filter(questionaire=q)

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['generic_privacy_targets'] = generic_privacy_targets
    args['selected_privacy_targets'] = selected_privacy_targets
    return render(request, "privacy_targets/privacy_target_identification.html", args)



@login_required
def privacy_target_delete(request, q_id=None, target_rel_id=None):
    '''
    Unselects a privacy target / Removes a privacy target from the user's list.
    '''
    # user = request.user
    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    privacy_target_rel = get_object_or_404(PrivacyQuestionaireRel, id=target_rel_id, questionaire=q)
    data = dict()
    if request.POST:
        privacy_target_rel.delete()
        ## ajax data
        django_messages = []
        messages.success(request, u'Privacy target "%s" was removed successfully.' %(privacy_target_rel.privacy_target))
        for message in messages.get_messages(request):
            django_messages.append({
                "level": message.level,
                "message": message.message,
                "extra_tags": message.tags,
            })
        data['form_is_valid'] = True
        data['messages'] = django_messages
        args = {}
        args['q'] = q
        args['privacy_q_rels'] = PrivacyQuestionaireRel.objects.select_related('questionaire', 'privacy_target').filter(questionaire=q)
        data['html_q_list'] = render_to_string('privacy_threats/partial_privacy_threats_list.html', args)
    else:
        args = {}
        args.update(csrf(request))
        args['q'] = q
        args['privacy_target_rel'] = privacy_target_rel
        data['html_form'] = render_to_string('privacy_targets/privacy_target_remove.html', args, request=request)
    return JsonResponse(data)
