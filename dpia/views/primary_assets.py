from dpia.modules import *
from dpia.views.generic_dicts import actors_dict

@login_required
def primary_list(request, q_id):
    '''
    Shows a list that contains only the primary assets which are added to a process of a usecase.
    '''
    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    ## check imported assets
    imported_assets = Primary.objects.filter(questionaire=q, is_imported=True)

    ### FORMSET PRIMARY ASSETS
    primaries = Primary.objects.filter(questionaire=q)
    ## primary asset formsets
    PrimaryFormset = modelformset_factory(Primary, form=PrimaryForm2, extra=0)
    primary_formset = PrimaryFormset(queryset=primaries)

    # dict of generic actors; needed for newly created dbs.
    actors = Actor.objects.all()
    if not actors.exists():
        for list in actors_dict.values():
            Actor.objects.get_or_create(name=list[0], description=list[1])


    if request.POST and "next_step" in request.POST:
        if primaries.exists() or imported_assets.exists():
            primary_formset = PrimaryFormset(request.POST)
            if primary_formset.is_valid():
                with reversion.create_revision():
                    ## Fill out primary assets
                    for form in primary_formset.forms:
                        primary = form.save(commit=False)
                        primary.save()
                    primary_formset.save()
                    # Store some meta-information.
                    primary_list = primaries.values_list('name', flat=True)
                    comment = ", ".join(primary_list)
                    save_revision_meta(user, q, 'Submited primary assets "{}".'.format(comment))
                    # update_q = Questionaire.objects.all().filter(id=q_id).update(step_likelihood=5) # update Questionaire Step
                    messages.success(request, u'Primary assets were updated successfully.')
                    return HttpResponseRedirect(reverse_lazy('threat_identification', args=[q.id]))
        else:
            return redirect('threat_identification', q.id)

        # else:
        #     # pass
        #     messages.error(request, u'Please fill out the required fields.')
        # else:
        #     messages.warning(request, u'Add primary and supporting assets.')

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['primaries'] = primaries
    args['primary_formset'] = primary_formset
    args['imported_assets'] = imported_assets
    return render(request, "primary_assets/primary_list.html", args)


@login_required
def primary_add(request, id=None):
    '''
    Adds a primary asset.
    '''
    queryuser = UserProfile.objects.all().filter(user=request.user)
    u = get_object_or_404(UseCase, questionaire__membership__member=queryuser, id=id)
    q = get_object_or_404(Questionaire, membership__member=queryuser, id=u.questionaire.id)
    # show all the generic actors and the the actors created in the instant questionaire
    actors = Actor.objects.all().exclude(~Q(usecase__questionaire=u.questionaire.id), usecase__questionaire__isnull=False)

    data = dict()
    with reversion.create_revision():
        if request.POST:
            primary_form = PrimaryForm(request.POST)
            primary_form.fields['data_subjects'].queryset = actors
            try:
                if primary_form.is_valid():
                    primary = primary_form.save(commit=False)
                    primary.questionaire = u.questionaire
                    primary.save()
                    ##reversion data
                    save_revision_meta(request.user, q, 'Added primary asset "%s".' %(primary.name))
                    ## ajax data
                    django_messages = []
                    messages.success(request, u'  Primary Asset "%s" was added successfully.' %(primary.name))
                    for message in messages.get_messages(request):
                        django_messages.append({
                            "level": message.level,
                            "message": message.message,
                            "extra_tags": message.tags,
                        })
                    data['messages'] = django_messages
                    data['id'] = primary.id
                    data['name'] = primary.name
                    data['form_is_valid'] = True
                else:
                    data['form_is_valid'] = False
            ## catch the IntegrityError thrown by the unique_together constraint.
            except IntegrityError: ## as e
                msg = "Primary Asset with this name already exists for this questionaire"
                primary_form.add_error('name', msg) ## e.__cause__
        else:
            primary_form = PrimaryForm()
            primary_form.fields['data_subjects'].queryset = actors

    args = {}
    args.update(csrf(request))
    args['primary_form'] = primary_form
    args['u'] = u
    data['html_form'] = render_to_string('primary_assets/primary_add.html', args, request=request)
    return JsonResponse(data)


@login_required
def primary_list_add(request, q_id=None):
    '''
    Adds a primary asset.
    '''
    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    # show all the generic actors and the the actors created in the instant questionaire
    actors = Actor.objects.all().exclude(~Q(usecase__questionaire=q.id), usecase__questionaire__isnull=False)

    data = dict()
    with reversion.create_revision():
        if request.POST:
            primary_form = PrimaryForm(request.POST)
            primary_form.fields['data_subjects'].queryset = actors
            try:
                if primary_form.is_valid():
                    primary = primary_form.save(commit=False)
                    primary.questionaire = q
                    primary.save()
                    ##reversion data
                    save_revision_meta(request.user, q, 'Added primary asset "%s".' %(primary.name))
                    ## ajax data
                    django_messages = []
                    messages.success(request, u'  Primary Asset "%s" was added successfully.' %(primary.name))
                    for message in messages.get_messages(request):
                        django_messages.append({
                            "level": message.level,
                            "message": message.message,
                            "extra_tags": message.tags,
                        })
                    data['messages'] = django_messages
                    data['form_is_valid'] = True

                    ### FORMSET PRIMARY ASSETS
                    primaries = Primary.objects.select_related('questionaire', 'data_subjects').prefetch_related('primary_in_psrel', 'primary_in_psrel__supporting').filter(questionaire=q)
                    ## primary asset formsets
                    PrimaryFormset = modelformset_factory(Primary, form=PrimaryForm2, extra=0)
                    primary_formset = PrimaryFormset(queryset=primaries)
                    data['html_q_list'] = render_to_string('primary_assets/partial_primary_list.html', {'primary_formset': primary_formset})
                else:
                    data['form_is_valid'] = False
            ## catch the IntegrityError thrown by the unique_together constraint.
            except IntegrityError: ## as e
                msg = "Primary Asset with this name already exists for this questionaire"
                primary_form.add_error('name', msg) ## e.__cause__
        else:
            primary_form = PrimaryForm()
            primary_form.fields['data_subjects'].queryset = actors

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['primary_form'] = primary_form
    data['html_form'] = render_to_string('primary_assets/primary_add.html', args, request=request)
    return JsonResponse(data)

@login_required
def primary_edit(request, primary_id):
    '''
    Edits a primary asset in the primary asset list.
    '''
    user = request.user
    primary = get_object_or_404(Primary, questionaire__q_in_membership__member=user, id=primary_id)
    q = get_object_or_404(Questionaire, id=primary.questionaire_id)
    actors = Actor.objects.all().exclude(~Q(usecase__questionaire=q), usecase__questionaire__isnull=False)

    data = dict()

    primary_form = PrimaryForm(request.POST or None, instance=primary)
    primary_form.fields['data_subjects'].queryset = actors

    try:
        if primary_form.is_valid():
            with reversion.create_revision():
                primary_form.save()
                # Store some meta-information.
                save_revision_meta(request.user, q, 'Changed details of primary asset "%s".' %(primary.name))
                ## json data
                ## ajax data
                django_messages = []
                messages.success(request, u'  Primary Asset "%s" was changed successfully.' %(primary.name))
                for message in messages.get_messages(request):
                    django_messages.append({
                        "level": message.level,
                        "message": message.message,
                        "extra_tags": message.tags,
                    })
                data['messages'] = django_messages
                data['form_is_valid'] = True

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
        msg = "Primary asset with this Name already exists for this Questionaire"
        primary_form.add_error('name', msg) ## e.__cause__

    args = {}
    args.update(csrf(request))
    args['primary_form'] = primary_form
    args['primary'] = primary
    data['html_form'] = render_to_string('primary_assets/primary_edit.html', args, request=request)
    return JsonResponse(data)



@login_required
def primary_process_edit(request, primary_id=None, u_id=None):
    '''
    Edits a primary asset in the "usecase_details" list.
    '''
    primary = get_object_or_404(Primary, questionaire__q_in_membership__member=request.user, id=primary_id)
    q = get_object_or_404(Questionaire, id=primary.questionaire_id)
    u = get_object_or_404(UseCase, id=u_id)
    actors = Actor.objects.all().exclude(~Q(usecase__questionaire=q), usecase__questionaire__isnull=False)

    data = dict()

    primary_form = PrimaryForm(request.POST or None, instance=primary)
    with reversion.create_revision():
        if request.POST:
            try:
                if primary_form.is_valid():
                    primary_form.save()
                    # Store some meta-information.
                    save_revision_meta(request.user, q, 'Changed primary asset "%s".' %(primary.name))
                    ## json data
                    saved_primaries = Primary.objects.filter(questionaire__usecase=u).distinct()
                    # data['id'] = primary.id
                    # data['name'] = primary.name
                    data['form_is_valid'] = True

                    data['primaries'] = saved_primaries
                    data['html_primary_list'] = render_to_string('usecases/usecase_scenario.html', {'saved_primaries': saved_primaries})
                else:
                    data['form_is_valid'] = False
            ## catch the IntegrityError thrown by the unique_together constraint.
            except IntegrityError as e: ## as e
                msg = "Primary asset with this name already exists for this questionaire"
                primary_form.add_error('name', e.__cause__) ## e.__cause__
        else:
            primary_form.fields['data_subjects'].queryset = actors


    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['u'] = u
    args['primary'] = primary
    args['primary_form'] = primary_form
    data['html_form'] = render_to_string('primary_assets/primary_process_edit.html', args, request=request)
    return JsonResponse(data)


@login_required
def primary_delete(request, primary_id=None):
    '''
    Deletes a primary asset.
    '''
    user = request.user
    primary = get_object_or_404(Primary, id=primary_id)
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=primary.questionaire_id)
    pa_sa = PrimarySupportingRel.objects.filter(primary=primary)
    sa = Supporting.objects.filter(questionaire=q, primary__primary=primary.id)

    data = dict()

    primary.delete()
    sa.delete()

    ## ajax data
    django_messages = []
    messages.success(request, u'  Primary asset "%s" was deleted successfully.' %(primary.name))
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
    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['primary_formset'] = primary_formset
    data['html_q_list'] = render_to_string('primary_assets/partial_primary_list.html', args, request=request)

    return JsonResponse(data)
