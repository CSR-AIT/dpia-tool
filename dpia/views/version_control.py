from dpia.modules import *

### RECOVER/REVERT/Version Control ###
@login_required
def deleted_questionnaires(request):
    # Build a list of all deleted questionnaires, latest versions first:
    deleted_questionnaires = Version.objects.get_deleted(Questionaire).select_related('revision', 'revision__versionowner').filter(revision__versionowner__owner_id=request.user.id)
    args = {}
    args.update(csrf(request))
    args['deleted_questionnaires'] = deleted_questionnaires
    return render(request, "version_control/deleted_qs.html", args)

@login_required
def recover_questionnaire(request, q_id=None):
    # Build a list of all previous versions, latest versions first:
    deleted_questionnaires = Version.objects.get_deleted(Questionaire).select_related('revision', 'revision__versionowner').filter(revision__versionowner__owner_id=request.user.id)
    # Access a specific deleted object.
    deleted_q = deleted_questionnaires.get(id=q_id)

    # Revert the first revision.
    if deleted_q.revision.versionowner.owner_id == request.user.id:
        try:
            deleted_q.revision.revert()
            messages.success(request, u'Questionnaire "%s" was recovered successfully.' %(deleted_q))
            return redirect('dashboard')
        except ValueError:
            messages.warning(request, u'There was some problem recovering your questionnaire.')
            return redirect('deleted_questionnaires')
    else:
        return HttpResponseForbidden("You are not allowed to perform this action!")


## Versions of the questionnaire ##
# versions of each instance

@login_required
@auth_required
def history(request, q_id=None):
    q = get_object_or_404(Questionaire, id=q_id)
    # version_list = Version.objects.get_for_object_reference(Questionaire, q.id, model_db=None).select_related('revision', 'revision__versionowner', 'revision__user').filter(revision__versionowner__owner_id=request.user.id)
    version_list = Version.objects.select_related('revision', 'revision__versionowner', 'revision__user').filter(revision__versionowner__owner_id=request.user.id).get_for_object(q)
    # if version_list.exists():
    #     version_list = version_list[:len(version_list)-1]
    # get the path of the page where the button is clicked.
    get_path = request.POST.get('next')
    paginator = Paginator(version_list, 20)
    page = request.GET.get('page')
    try:
        versions = paginator.page(page)
    except PageNotAnInteger:
        versions = paginator.page(1)
    except EmptyPage:
        versions = paginator.page(paginator.num_pages)

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['versions'] = versions
    args['get_path'] = get_path
    return render(request, "version_control/history.html", args)


@login_required
@auth_required
def revert_version(request, q_id=None, revision_id=None):
    q = get_object_or_404(Questionaire, id=q_id)
    try:
        # version = get_object_or_404(Version.objects.select_related('revision', 'content_type'), pk=version_id, object_id=q_id)
        revision = get_object_or_404(Revision.objects.select_related('user', 'versionowner').prefetch_related('version_set'), id=revision_id)
        revision.version_set.all()
        revision.revert(delete=False) # when True, deletes all the objects added after the time of the selected action.
        # with reversion.create_revision():
        #     #revision.version_set.all()
        #     revision.revert(delete=True)
        #     save_revision_meta(request.user, q, "Restored to version number {}.".format(revision_id))
        # # version_datetime = version_datetime.strftime("%d/%m/%y, %H:%M")
        # get the path of the page where the button is clicked.
        get_path = request.POST.get('next')
        if request.POST and 'revert_button' in request.POST:
            messages.success(request, u'Questionnaire "%s" was reverted successfully to version nr. %s.' %(q, revision.id))
            if get_path:
                return HttpResponseRedirect(get_path)
            else:
                return redirect(reverse('history', args=[q.id]))
        else:
            messages.success(request, u'Questionnaire "%s" was reverted successfully to version nr. %s.' %(q, revision.id))
            return redirect(reverse('history', args=[q.id]))

    except ValueError:
        messages.warning(request, 'There was some error. Please try to revert another version of the questionnaire.')
        return redirect('history', q.id)
