from dpia.modules import *


@login_required
def members(request, q_id):
    '''
    Shows the list of members of a questionnaire.
    '''

    user = request.user
    q = get_object_or_404(Questionaire, id=q_id)
    memberships = Membership.objects.select_related('questionaire', 'member').filter(questionaire_id=q_id)

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['user'] = user
    args['memberships'] = memberships
    return render(request, 'members/member_list.html', args)



@login_required
@auth_required
def member_add(request, q_id):
    '''
    Adds a member.
    Only the owner can add new members.
    '''

    user = request.user
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=q_id)
    user_list = User.objects.exclude(id=user.id).exclude(questionaire=q)

    data = dict()

    if request.POST:
        # Declare a revision block.
        if 'user' in request.POST:
            with reversion.create_revision():
                checked_users = request.POST.getlist('user')
                users_list = []
                for checked_user in checked_users:
                    user_object = get_object_or_404(User, id=checked_user)
                    # create a new relationship with the above objects, no duplicates
                    rel, created = Membership.objects.get_or_create(questionaire=q, member=user_object, is_owner=False)
                    users_list.append(user_object.username)
                # Store some meta-information.
                comment = 'Added team members "{}".'.format(", ".join(users_list))
                save_revision_meta(user, q, comment)
                ## ajax data
                django_messages = []
                messages.success(request, u'Members were added successfully.')
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
                args['memberships'] = Membership.objects.select_related('member', 'questionaire').filter(questionaire=q)
                data['html_q_list'] = render_to_string('members/partial_member_list.html', args, request=request)
        else:
            data['form_is_valid'] = False


    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['user_list'] = user_list
    data['html_form'] = render_to_string('members/member_add.html', args, request=request)
    return JsonResponse(data)


@login_required
def member_edit(request, q_id=None, membership_id=None):
    '''
    Edits a member.
    The owner of the questionnaire can edit all the members, and each member can edit only themselves.
    '''

    user = request.user
    q = get_object_or_404(Questionaire, id=q_id)
    membership = get_object_or_404(Membership, id=membership_id)
    ownership = get_object_or_404(Membership, questionaire=q, is_owner=True)
    # users = UserProfile.objects.select_related('user').prefetch_related('member_of').filter(user_id=membership.member_id)
    members_name = membership.member.get_full_name()
    members_responsibility_old = membership.responsibility_in_dpia

    data = dict()

    form = MembershipForm(request.POST or None, instance=membership)
    if ownership.member == user or (not membership.is_owner and membership.member == user):
        if request.POST:
            if form.is_valid():
                with reversion.create_revision():
                    form.save()
                    # Store some meta-information.
                    save_revision_meta(request.user, q, 'Changed responsibility of member "%s" from "%s" to "%s".' %(members_name, members_responsibility_old, membership.responsibility_in_dpia))
                    ## ajax data
                    django_messages = []
                    messages.success(request, u'Responsibility of member "%s" was changed successfully from "%s" to "%s".' %(membership.member.get_full_name(), members_responsibility_old, membership.responsibility_in_dpia))
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
                    args['memberships'] = Membership.objects.select_related('member').filter(questionaire=q)
                    data['html_q_list'] = render_to_string('members/partial_member_list.html', args, request=request)
            else:
                data['form_is_valid'] = False
    else:
        return HttpResponseForbidden(u'You have no permission to edit member "%s".' %(membership.member.get_full_name()))

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['membership'] = membership
    args['form'] = form
    data['html_form'] = render_to_string('members/member_edit.html', args, request=request)
    return JsonResponse(data)


@login_required
@auth_required
def member_delete(request, q_id=None, membership_id=None):
    '''
    Removes a member from a questionnaire.
    Only owners of the questionnaire are allowed to do this.
    '''

    user = request.user
    q = get_object_or_404(Questionaire, id=q_id)
    membership = get_object_or_404(Membership, id=membership_id)
    ownership = get_object_or_404(Membership, is_owner=True, questionaire=q)

    data = dict()


    if membership.is_owner == False:
        if request.POST and request.is_ajax():
            # try:
            membership.delete()
            ## ajax data
            django_messages = []
            messages.success(request, u'Member "%s" was removed successfully.' %(membership.member.get_full_name()))
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
            args['memberships'] = Membership.objects.select_for_update().select_related('questionaire', 'member').filter(questionaire=q)
            data['html_q_list'] = render_to_string('members/partial_member_list.html', args, request=request)
            # catch IntegrityError
            # except PageNotFound, error:
            #     messages.error(request, u'You have no permission to delete members.')
            #     return HttpResponseRedirect(reverse('members', args=[q.id]))
        else:
            args = {}
            args.update(csrf(request))
            args['q'] = q
            args['membership'] = membership
            data['html_form'] = render_to_string('members/member_remove.html', args, request=request)
        return JsonResponse(data)

    else:
        return HttpResponseForbidden("You are not allowed to remove yourself from the questionnaire you created! Your ownership can be terminated only if you remove the questionnaire.")
