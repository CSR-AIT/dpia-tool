from dpia.modules import *


@login_required
def usecases(request, id):
    '''
    Shows a list of usecases.
    '''

    q = get_object_or_404(Questionaire, membership__member__user=request.user, id=id)
    #query the saved usecases
    saved_usecases = UseCase.objects.select_related('questionaire').prefetch_related('process').filter(questionaire=q)
    # query the processes of this questionnaire // next step activation
    saved_processes = Process.objects.select_related('usecase__questionaire').filter(usecase__questionaire=q)

    # if not saved_usecases.exists():
    #     q.step_usecase=0
    #     q.save()
    #
    # if not saved_processes.exists():
    #     q.step_process=0
    #     q.save()

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['saved_usecases'] = saved_usecases
    args['saved_processes'] = saved_processes
    return render(request, "usecases/usecases.html", args)



@login_required
def add_usecase(request, id=None):
    '''
    Adds a usecase.
    '''
    queryuser = UserProfile.objects.all().filter(user=request.user)
    q = get_object_or_404(Questionaire, membership__member=queryuser, id=id)

    data = dict()
    usecase_form = UseCaseForm(request.POST or None)
    with reversion.create_revision():
        if request.POST:
            if usecase_form.is_valid():
                u = usecase_form.save(commit=False)
                u.questionaire = q
                u.save()
                # Store some meta-information.
                save_revision_meta(request.user, q, "Added use case '%s'." %(u.name))

                ## ajax data
                django_messages = []
                messages.success(request, u'  Use case "%s" was added successfully.' %(u.name))
                for message in messages.get_messages(request):
                    django_messages.append({
                        "level": message.level,
                        "message": message.message,
                        "extra_tags": message.tags,
                    })
                data['form_is_valid'] = True
                data['messages'] = django_messages

                #query the saved sources
                saved_usecases = UseCase.objects.select_related('questionaire').prefetch_related('process').filter(questionaire=q)
                args = {}
                args['saved_usecases'] = saved_usecases
                data['html_q_list'] = render_to_string('usecases/partial_usecase_list.html', args, request=request)
            else:
                data['form_is_valid'] = False

    args = {}
    args.update(csrf(request))
    args['form'] = usecase_form
    args['q'] = q
    data['html_form'] = render_to_string('usecases/usecase_add.html', args, request=request)
    return JsonResponse(data)



@login_required
def edit_usecase(request, id=None):
    '''
    Edits a usecase.
    '''
    queryuser = UserProfile.objects.all().filter(user=request.user)
    u = get_object_or_404(UseCase, questionaire__membership__member=queryuser, id=id)
    q = get_object_or_404(Questionaire, membership__member=queryuser, id=u.questionaire_id)
    current_url = resolve(request.path_info).url_name

    data = dict()

    form = UseCaseForm(request.POST or None, instance=u)
    with reversion.create_revision():
        if request.POST:
            if form.is_valid():
                form.save()
                # Store some meta-information.
                save_revision_meta(request.user, q, 'Changed use case %s.' %(u.name))
                ## ajax data
                django_messages = []
                messages.success(request, u'  Use case "%s" was changed successfully.' %(u.name))
                for message in messages.get_messages(request):
                    django_messages.append({
                        "level": message.level,
                        "message": message.message,
                        "extra_tags": message.tags,
                    })
                data['form_is_valid'] = True
                data['messages'] = django_messages

                #query the saved sources
                saved_usecases = UseCase.objects.select_related('questionaire').prefetch_related('process').filter(questionaire=q)
                args = {}
                args['q'] = q
                args['saved_usecases'] = saved_usecases
                data['html_q_list'] = render_to_string('usecases/partial_usecase_list.html', args, request=request)

            else:
                data['form_is_valid'] = False

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['u'] = u
    args['form'] = form
    data['html_form'] = render_to_string('usecases/usecase_edit.html', args, request=request)
    return JsonResponse(data)


@login_required
def delete_usecase(request, id=None):
    '''
    Deletes a usecase.
    '''
    queryuser = UserProfile.objects.all().filter(user=request.user)
    u = get_object_or_404(UseCase, id=id)
    q = get_object_or_404(Questionaire, membership__member=queryuser, id=u.questionaire_id)

    data = dict()


    if request.POST:
        u.delete()
        ## ajax data
        django_messages = []
        messages.success(request, u'  Use case "%s" was deleted successfully.' %(u.name))
        for message in messages.get_messages(request):
            django_messages.append({
                "level": message.level,
                "message": message.message,
                "extra_tags": message.tags,
            })
        data['form_is_valid'] = True
        data['messages'] = django_messages
        #query the saved sources
        saved_usecases = UseCase.objects.select_related('questionaire').prefetch_related('process').filter(questionaire=q)

        args = {}
        args['q'] = q
        args['saved_usecases'] = saved_usecases
        data['html_q_list'] = render_to_string('usecases/partial_usecase_list.html', args, request=request)
    else:
        args = {}
        args.update(csrf(request))
        args['q'] = q
        args['u'] = u
        data['html_form'] = render_to_string('usecases/usecase_delete.html', args, request=request)
    return JsonResponse(data)



@login_required
def usecase_scenario(request, id):
    '''
    Shows the information details of a usecase, and an empty formset of processes that are related to the scenario of that usecase.
    '''

    u = get_object_or_404(UseCase.objects.select_related('questionaire').prefetch_related('actor'), questionaire__membership__member__user=request.user, id=id)
    print(u.description)
    #query the questionnaire of this usecase
    q = get_object_or_404(Questionaire, membership__member__user=request.user, id=u.questionaire_id)

    # query the processes of Use Case
    saved_processes = Process.objects.select_related('usecase', 'information_exchanged', 'information_producer', 'information_receiver').filter(usecase=u)
    # show all the generic actors and the the actors created in the instant questionaire
    actors = Actor.objects.select_related('usecase', 'usecase__questionaire').exclude(~Q(usecase__questionaire=q), usecase__questionaire__isnull=False)
    # print(actors)
    # show all the primary assets created in the instant questionaire
    primaries = Primary.objects.select_related('questionaire', 'data_subjects').filter(questionaire=q)

    ## ADD PROCESSES
    ProcessFormset = modelformset_factory(Process, form=ProcessForm, extra=1, max_num=1)

    with reversion.create_revision():
        if request.POST:
            if '_save' in request.POST:
                process_formset = ProcessFormset(request.POST, queryset=saved_processes)
                for form in process_formset.forms:
                    form.fields['information_producer'].queryset = actors
                    form.fields['information_receiver'].queryset = actors
                    form.fields['information_exchanged'].queryset = primaries
                try:
                    if process_formset.is_valid():
                        for form in process_formset.forms:
                            process = form.save(commit=False)
                            process.usecase = u
                            process.save()
                        process_formset.save()
                        form_count = process_formset.total_form_count()

                        # Store some meta-information.
                        save_revision_meta(request.user, q, 'Added %s process(es) to usecase "%s".' %(form_count, u.name))
                        if form_count == 1:
                            messages.success(request, u'Process was added successfully.')
                        else:
                            messages.success(request, u'Processes were added successfully.')
                        return HttpResponseRedirect(reverse_lazy('usecase_details', args=[u.id]))
                    else:
                        pass
                except IntegrityError as e:
                    messages.error(request, e)

        else:
            process_formset = ProcessFormset(queryset=saved_processes)
            for form in process_formset.forms:
                form.fields['information_producer'].queryset = actors
                form.fields['information_receiver'].queryset = actors
                form.fields['information_exchanged'].queryset = primaries


    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['u'] = u
    args['process_formset'] = process_formset
    args['saved_processes'] = saved_processes
    return render(request, "usecases/usecase_scenario.html", args)



@login_required
def process_delete(request, id=None):
    '''
    Removes process.
    '''
    process = get_object_or_404(Process, id=id)
    u = get_object_or_404(UseCase, id=process.usecase.id)
    q = get_object_or_404(Questionaire, membership__member__user=request.user, id=u.questionaire_id)
    #query the processes of Use Case
    saved_processes = Process.objects.select_related('usecase', 'information_exchanged', 'information_producer', 'information_receiver').filter(usecase__questionaire=q)

    if request.POST:
        process.delete()
        messages.success(request, u'Process "%s" was removed successfully.' %(process.description))
        return HttpResponseRedirect(reverse('usecase_details', args=[u.id]))


    args = {}
    args.update(csrf(request))
    args['process'] = process
    args['u'] = u
    return render(request, 'usecases/process_delete.html', args)


@login_required
def actor_add(request, id=None):
    '''
    Adds an actor.
    '''
    queryuser = UserProfile.objects.all().filter(user=request.user)
    u = get_object_or_404(UseCase, questionaire__membership__member=queryuser, id=id)
    q = get_object_or_404(Questionaire, membership__member=queryuser, id=u.questionaire_id)

    data = dict()

    # Add-Actor-Form
    with reversion.create_revision():
        if request.POST:
            actor_form = ActorForm(request.POST)
            if actor_form.is_valid():
                actor = actor_form.save(commit=False)
                actor.usecase = u
                actor.save()
                ## reversion
                save_revision_meta(request.user, q, 'Added actor "%s".' %(actor.name))
                ## ajax data
                django_messages = []
                messages.success(request, u'  Actor "%s" was added successfully.' %(actor.name))
                for message in messages.get_messages(request):
                    django_messages.append({
                        "level": message.level,
                        "message": message.message,
                        "extra_tags": message.tags,
                    })
                data['messages'] = django_messages
                data['id'] = actor.id
                data['name'] = actor.name
                data['form_is_valid'] = True
            else:
                data['form_is_valid'] = False
        else:
            actor_form = ActorForm()

    args = {}
    args.update(csrf(request))
    args['actor_form'] = actor_form
    args['u'] = u
    data['html_form'] = render_to_string('usecases/actor_add.html', args, request=request)
    return JsonResponse(data)
