from dpia.modules import *

## login_required() decorator ensures that only those logged in can access the view.
@login_required()
def dashboard(request):
    '''
    This function shows the list of questionnaires the user has created or is assigned to.
    If the user hasn't created or isn't a simple member of another questionnaire, a link to create a new one is shown.
    '''

    user = request.user
    # get all the questionnaire memberships of the user
    user_memberships = Membership.objects.select_related('questionaire', 'member').filter(member=user)
    # get a list of all deleted questionnaires, latest first, for the template deleted-qs button
    #deleted_questionnaires = Version.objects.get_deleted(Questionaire).filter(revision__versionowner__owner_id=user.id).exists()

    args = {}
    args.update(csrf(request))
    args['user'] = user
    args['user_memberships'] = user_memberships
    #args['deleted_questionnaires'] = deleted_questionnaires
    return render(request, 'q/q_list.html', args)

@login_required
@pre_assessment_required
def q_add(request):
    '''
    Creates a new questionnaire. At the same time, the Pre-Assessment filled out before the user was directed to this page, is assigned to the created questionnaire.
    The questionnaire has only one owner: the user who created it.
    '''

    user = request.user
    user_answers = Answer.objects.filter(user=user, questionaire__isnull=True)

    if request.POST:
        # Declare a revision block.
        with reversion.create_revision():
            q_form = QuestionaireForm(request.POST)
            if q_form.is_valid():
                q = q_form.save(commit=False)
                q.save()
                for answer in user_answers:
                    answer.questionaire=q
                    answer.save()
                # user_answers.update(questionaire=q)
                # Store some meta-information.
                reversion.set_user(request.user)
                reversion.set_comment('Created questionnaire "%s".' %(q.description))
                membership = Membership.objects.create(questionaire=q, member=user, is_owner=True)
                reversion.add_meta(VersionOwner, owner_id=membership.member.id)
                messages.success(request, u'Questionnaire "%s" was created successfully.' %(q.description))
                return redirect('dashboard')
            else:
                pass
                # messages.error(request, q_form.errors)
    else:
        q_form = QuestionaireForm()

    args = {}
    args.update(csrf(request))
    args['q_form'] = q_form
    return render(request, 'q/q_add.html', args)



@login_required
@auth_required
def q_edit(request, q_id=None):
    '''
    Edits the questionnaire details.
    '''

    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    membership = get_object_or_404(Membership, member=user,  questionaire=q)
    old_q_name = q.description

    data = dict()

    # Declare a revision block.
    q_form = QuestionaireForm(request.POST or None, instance=q)
    if membership:
        if request.POST and request.is_ajax():
            with reversion.create_revision():
                if q_form.is_valid():
                    q_form.save()
                    # Store some meta-information.
                    save_revision_meta(user, q, 'Changed questionnaire details.')# from "{}" to "{}".'.format(old_q_name, q.description))
                    ## ajax data
                    django_messages = []
                    messages.success(request, u'Questionnaire "%s" was changed successfully.' %(q.description))
                    for message in messages.get_messages(request):
                        django_messages.append({
                            "level": message.level,
                            "message": message.message,
                            "extra_tags": message.tags,
                        })
                    data['form_is_valid'] = True
                    data['messages'] = django_messages
                    data['q_description'] = q.description
                    user_memberships = Membership.objects.select_related('questionaire', 'member').filter(member=user)
                    args = {}
                    args['user_memberships'] = user_memberships
                    data['html_q_list'] = render_to_string('q/q_partial_list.html', args, request=request)
                else:
                    data['form_is_valid'] = False
    else:
        messages.error(request, u'You have no permission to edit questionnaire "%s".' %(q.description))
        return redirect('dashboard')

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['q_form'] = q_form
    data['html_form'] = render_to_string('q/q_edit.html', args, request=request)
    return JsonResponse(data)



@login_required
@auth_required
def q_delete(request, q_id=None):
    '''
    Deletes a questionnaire, and every single objects related to it.
    '''

    user = request.user
    # gets the Qs of the User - where he clicks
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    data = dict()

    if request.POST:
        q.delete()
        messages.success(request, u'Questionnaire "%s" was deleted successfully.' %(q.description))
        return redirect('dashboard')
    else:
        args = {}
        args.update(csrf(request))
        args['q'] = q
        data['html_form'] = render_to_string('q/q_delete.html', args, request=request)
        return JsonResponse(data)
