from dpia.modules import *


# supporting-asset add
@login_required
def supporting_add(request, pa_id=None):
    '''
    Adds a supporting asset to a primary asset.
    '''
    user = request.user
    primary = get_object_or_404(Primary, questionaire__q_in_membership__member=user, id=pa_id)
    q = get_object_or_404(Questionaire, id=primary.questionaire_id)
    # query all the SA of the User
    supportings = Supporting.objects.filter(questionaire=q).distinct()

    data = dict()

    if request.POST and request.is_ajax():
        supporting_form = SupportingForm(request.POST)
        try:
            if supporting_form.is_valid():
                with reversion.create_revision():
                    s = supporting_form.save(commit=False)
                    s.questionaire = q
                    s.save()
                    rel, created = PrimarySupportingRel.objects.get_or_create(primary=primary, supporting=s)
                    # Store some meta-information.
                    save_revision_meta(user, q, 'Added supporting asset "%s" to primary asset "%s".' %(s, primary))
                    ## ajax data
                    django_messages = []
                    messages.success(request, u'Supporting asset "%s" was added successfully to primary asset "%s".' %(s, primary))
                    for message in messages.get_messages(request):
                        django_messages.append({
                            "level": message.level,
                            "message": message.message,
                            "extra_tags": message.tags,
                        })

                    data['form_is_valid'] = True
                    data['messages'] = django_messages
                    ### FORMSET PRIMARY ASSETS
                    primaries = Primary.objects.filter(questionaire=q)
                    ## primary asset formsets
                    PrimaryFormset = modelformset_factory(Primary, form=PrimaryForm2, extra=0)
                    primary_formset = PrimaryFormset(queryset=primaries)
                    data['html_q_list'] = render_to_string('primary_assets/partial_primary_list.html', {'primary_formset': primary_formset})
            else:
                data['form_is_valid'] = False
        ## catch the IntegrityError thrown by the unique_together constraint.
        except IntegrityError: ## as e
            msg = "Supporting asset with this description already exists for this questionaire"
            supporting_form.add_error('description', msg) ## e.__cause__
    else:
        supporting_form = SupportingForm()

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['primary'] = primary
    args['supportings'] = supportings
    args['supporting_form'] = supporting_form
    data['html_form'] = render_to_string('supporting_assets/supporting_add.html', args, request=request)
    return JsonResponse(data)




@login_required
def supporting_choose(request, pa_id=None):
    '''
    Selects a supporting asset from the added ones, and assigns it to a primary asset.
    '''
    user = request.user
    primary = get_object_or_404(Primary, questionaire__q_in_membership__member=user, id=pa_id)
    q = get_object_or_404(Questionaire, id=primary.questionaire_id)
    # query all the SA of the User
    supportings = Supporting.objects.filter(questionaire=q).distinct()

    data = dict()

    ## Add Threats to a SA

    if request.POST and request.is_ajax():
        if 'sa' in request.POST:
            with reversion.create_revision():
                checked_sas = request.POST.getlist('sa')
                sa_list = []
                for checked_sa in checked_sas:
                    sa_object = get_object_or_404(Supporting, id=checked_sa)
                    # create a new relationship with the above objects, no duplicates
                    rel, created = PrimarySupportingRel.objects.get_or_create(supporting=sa_object, primary=primary)
                    sa_list.append(rel.supporting.description)
                # Store some meta-information.
                comment = ", ".join(sa_list)
                save_revision_meta(user, q, 'Assigned supporting assets "%s" to primary asset "%s".' %(comment, primary))
                ## ajax data
                django_messages = []
                messages.success(request, u'Supporting assets were added successfully to primary asset "%s".' %(primary))
                for message in messages.get_messages(request):
                    django_messages.append({
                        "level": message.level,
                        "message": message.message,
                        "extra_tags": message.tags,
                    })
                data['form_is_valid'] = True
                data['messages'] = django_messages
                ### FORMSET PRIMARY ASSETS
                primaries = Primary.objects.filter(questionaire=q)
                ## primary asset formsets
                PrimaryFormset = modelformset_factory(Primary, form=PrimaryForm2, extra=0)
                primary_formset = PrimaryFormset(queryset=primaries)
                data['html_q_list'] = render_to_string('primary_assets/partial_primary_list.html', {'primary_formset': primary_formset})
        else:
            data['form_is_valid'] = False
    else:
        supporting_form = SupportingForm()

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['primary'] = primary
    args['supportings'] = supportings
    data['html_form'] = render_to_string('supporting_assets/supporting_choose.html', args, request=request)
    return JsonResponse(data)



@login_required
def supporting_edit(request, sa_id=None):
    '''
    Edits a supporting asset.
    '''
    user = request.user
    supporting_rel = get_object_or_404(PrimarySupportingRel, primary__questionaire__q_in_membership__member=user, id=sa_id)
    supporting = get_object_or_404(Supporting, id=supporting_rel.supporting_id)
    q = get_object_or_404(Questionaire, id=supporting_rel.primary.questionaire_id)

    data = dict()

    if request.POST and request.is_ajax():
        supporting_form = SupportingForm(request.POST, instance=supporting)
        try:
            if supporting_form.is_valid():
                with reversion.create_revision():
                    supporting_form.save()
                    # Store some meta-information.
                    save_revision_meta(user, q, 'Changed details of supporting asset "%s".' %(supporting_form.instance.description))
                    ## ajax data
                    django_messages = []
                    messages.success(request, u'Supporting asset "%s" was changed successfully.' %(supporting_form.instance.description))
                    for message in messages.get_messages(request):
                        django_messages.append({
                            "level": message.level,
                            "message": message.message,
                            "extra_tags": message.tags,
                        })
                    data['form_is_valid'] = True
                    data['messages'] = django_messages

                    ### FORMSET PRIMARY ASSETS
                    primaries = Primary.objects.filter(questionaire=q)
                    ## primary asset formsets
                    PrimaryFormset = modelformset_factory(Primary, form=PrimaryForm2, extra=0)
                    primary_formset = PrimaryFormset(queryset=primaries)
                    data['html_q_list'] = render_to_string('primary_assets/partial_primary_list.html', {'primary_formset': primary_formset})
            else:
                data['form_is_valid'] = False
        ## catch the IntegrityError thrown by the unique_together constraint.
        except IntegrityError: ## as e
            msg = "Supporting asset with this description already exists for this questionaire"
            supporting_form.add_error('description', msg) ## e.__cause__
    else:
        supporting_form = SupportingForm(instance=supporting)

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['supporting_rel'] = supporting_rel
    args['supporting'] = supporting
    args['supporting_form'] = supporting_form
    data['html_form'] = render_to_string('supporting_assets/supporting_edit.html', args, request=request)
    return JsonResponse(data)




@login_required
def supporting_rel_delete(request, sa_id):
    '''
    Deletes a supporting asset.
    '''
    user = request.user
    # query the clicked to delete Rel
    supporting_rel = get_object_or_404(PrimarySupportingRel, primary__questionaire__q_in_membership__member=user, id=sa_id)
    q = get_object_or_404(Questionaire, id=supporting_rel.primary.questionaire_id)

    data = dict()

    if request.POST and request.is_ajax():
        supporting_rel.delete()
        ## ajax data
        django_messages = []
        messages.success(request, u'Supporting asset "%s" was removed successfully.' %(supporting_rel.supporting))
        for message in messages.get_messages(request):
            django_messages.append({
                "level": message.level,
                "message": message.message,
                "extra_tags": message.tags,
            })
        data['form_is_valid'] = True
        data['messages'] = django_messages

        ### FORMSET PRIMARY ASSETS
        primaries = Primary.objects.filter(questionaire=q)
        ## primary asset formsets
        PrimaryFormset = modelformset_factory(Primary, form=PrimaryForm2, extra=0)
        primary_formset = PrimaryFormset(queryset=primaries)
        data['html_q_list'] = render_to_string('primary_assets/partial_primary_list.html', {'primary_formset': primary_formset})
    else:
        args = {}
        args.update(csrf(request))
        args['q'] = q
        args['supporting_rel'] = supporting_rel
        data['html_form'] = render_to_string('supporting_assets/supporting_rel_delete.html', args, request=request)
    return JsonResponse(data)
