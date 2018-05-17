from dpia.modules import *

@login_required
def sources(request, q_id):
    '''
    Shows a list of the sources related to a particular questionnaire.
    '''
    # gets the Qs of the User
    q = get_object_or_404(Questionaire, q_in_membership__member=request.user, id=q_id)
    #query the saved sources
    sources = SourceInventory.objects.filter(questionaire=q)

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['sources'] = sources
    return render(request, "sources/sources.html", args)



@login_required
def add_source(request, q_id=None):
    '''
    Adds a source.
    '''
    data = dict()
    user = request.user
    q = get_object_or_404(Questionaire.objects.prefetch_related('q_in_membership'), q_in_membership__member=user, id=q_id)

    source_form = SourceInventoryForm(request.POST or None, request.FILES or None)
    if source_form.is_valid():
        # Declare a revision block.
        with reversion.create_revision():
            source = SourceInventory(source_file=request.FILES.get('source_file'))
            source = source_form.save(commit=False)
            source.questionaire = q
            source.uploaded_by = user
            source.save()
            # Store some meta-information.
            # get only the name of the source file, not the full path
            if source.source_file:
                source_file_name = os.path.basename(source.source_file.path)
                comment = 'Added source "%s" and source file "%s".' %(source.name, source_file_name)
            else:
                comment = 'Added source "%s" without source file.' %(source.name)
            save_revision_meta(user, q, comment)
            ## ajax data
            django_messages = []
            messages.success(request, u'  Source "%s" was added successfully.' %(source.name))
            for message in messages.get_messages(request):
                django_messages.append({
                    "level": message.level,
                    "message": message.message,
                    "extra_tags": message.tags,
                })

            data['form_is_valid'] = True
            data['messages'] = django_messages
            args = {}
            sources =  SourceInventory.objects.filter(questionaire=q)
            args['sources'] = sources
            data['html_source_list'] = render_to_string('sources/partial_source_list.html', args, request=request)
    else:
        data['form_is_valid'] = False


    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['source_form'] = source_form
    data['html_form'] = render_to_string('sources/source_add.html', args, request=request)
    return JsonResponse(data)



@login_required
def edit_source(request, source_id=None):
    '''
    Edits a source.
    '''
    data = dict()
    user = request.user
    source = get_object_or_404(SourceInventory, id=source_id)
    q = get_object_or_404(Questionaire, q_in_membership__member=user, id=source.questionaire_id)

    source_form = SourceInventoryForm(request.POST or None, request.FILES or None, instance=source)

    if source_form.is_valid():
        # Declare a revision block.
        with reversion.create_revision():
            source = source_form.save(commit=False)
            source.uploaded_by = user
            source.save()
            # Store some meta-information.
            # get only the name of the source file, not the full path
            if source.source_file:
                source_file_name = os.path.basename(source.source_file.path)
                comment = 'Changed details of source "%s" and changed/added source file "%s".' %(source.name, source_file_name)
            else:
                comment = 'Changed details of source "%s".' %(source.name)

            save_revision_meta(user, q, comment)
            ## ajax data
            django_messages = []
            messages.success(request, u'  Source "%s" was changed successfully.' %(source.name))
            for message in messages.get_messages(request):
                django_messages.append({
                    "level": message.level,
                    "message": message.message,
                    "extra_tags": message.tags,
                })

            data['form_is_valid'] = True
            data['messages'] = django_messages
            sources = SourceInventory.objects.filter(questionaire=q)
            data['html_source_list'] = render_to_string('sources/partial_source_list.html', {'sources': sources})
    else:
        data['form_is_valid'] = False

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['source'] = source
    args['source_form'] = source_form
    data['html_form'] = render_to_string('sources/source_edit.html', args, request=request)
    return JsonResponse(data)



@login_required
def delete_source(request, source_id=None):
    '''
    Deletes a source.
    '''
    user = request.user
    data = dict()
    source = get_object_or_404(SourceInventory, id=source_id)
    q = get_object_or_404(Questionaire, id=source.questionaire_id)
    # Declare a revision block.
    with reversion.create_revision():
        if request.POST:
            source.delete()
            # Store some meta-information.
            reversion.set_user(user)
            reversion.set_comment("Deleted source '%s'." %(source.name))
            ownership = get_object_or_404(Membership, questionaire=q, is_owner=True)
            owner = ownership.member.username
            reversion.add_meta(VersionOwner, owner=owner)
            ## ajax data
            django_messages = []
            messages.success(request, u'  Source "%s" was deleted successfully.' %(source.name))
            for message in messages.get_messages(request):
                django_messages.append({
                    "level": message.level,
                    "message": message.message,
                    "extra_tags": message.tags,
                })
            data['form_is_valid'] = True
            data['messages'] = django_messages
            args = {}
            args['sources'] = SourceInventory.objects.filter(questionaire=q)
            data['html_source_list'] = render_to_string('sources/partial_source_list.html', args, request=request)
        else:
            args = {}
            args.update(csrf(request))
            args['q'] = q
            args['source'] = source
            data['html_form'] = render_to_string('sources/source_delete.html', args, request=request)
        return JsonResponse(data)


from django.conf import settings
## download the source file
def download_source_file(request, q_id=None, file_url=None):
    '''
    Downloads the source file added by the user.
    '''
    file_path = os.path.join(settings.MEDIA_ROOT, file_url)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Length'] = os.stat(file_path).st_size
            response['Content-Disposition'] = 'attachment; filename = %s' % os.path.basename(file_path)
            return response
    else:
        messages.warning(request, 'File not found!')
        return redirect('sources', q_id)


#delete also the file of the source being deleted
# @receiver(post_delete, sender=SourceInventory)
# def post_delete_source_file(sender, instance, *args, **kwargs):
#     '''
#     Deletes the file associated with the source being deleted.
#     '''
#     if instance.source_file:
#         instance.source_file.delete(save=False)


def source_file_delete(request, q_id=None, source_id=None):
    q = get_object_or_404(Questionaire, id=q_id)
    source = get_object_or_404(SourceInventory, questionaire=q, id=source_id)
    if source.source_file:
        source.source_file.delete(save=False)
        return redirect('sources', q.id)
    else:
        messages.warning(request, 'Source has no file to delete.')
        return redirect('sources', q.id)

### Import-Export Sources
## Export
def export_data(request, q_id=None):
    q = get_object_or_404(Questionaire, id=q_id)
    format_form = ExportFormatForm(request.POST or None)
    if request.POST and "_export" in request.POST:
        if format_form.is_valid():
            file_format_code = request.POST.get('file_format')
            source_resource = SourceResource()
            sources = SourceInventory.objects.select_related('questionaire').filter(questionaire=q_id)
            dataset = source_resource.export(sources)
            if file_format_code == "1":
                response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename="sources.xls"'
                return response
            elif file_format_code == "2":
                response = HttpResponse(dataset.json, content_type='application/json')
                response['Content-Disposition'] = 'attachment; filename="sources.json"'
                return response
            elif file_format_code == "3":
                response = HttpResponse(dataset.csv, content_type='application/csv')
                response['Content-Disposition'] = 'attachment; filename="sources.csv"'
                return response
        else:
            messages.error(request, u'Error.')

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['format_form'] = format_form
    return render(request, "sources/sources_export.html", args)


## Import
def import_data(request, q_id=None):
    q = get_object_or_404(Questionaire, id=q_id)
    source_resource = SourceResource()
    if request.POST and "_import" in request.POST:
        dataset = Dataset()
        new_sources = request.FILES['source_file']
        imported_data = dataset.load(new_sources.read())
        result = source_resource.import_data(dataset, dry_run=True) # Test the data import
        if not result.has_errors():
            source_resource.import_data(dataset, dry_run=False) # Actually import now
            messages.success(request, u'Sources were imported successfully.')
            return HttpResponseRedirect(reverse('sources', args=[q_id] ))
        else:
            messages.error(request, u'%s' %(result))
            return HttpResponseRedirect(reverse('import_data', args=[q_id] ))


    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['source_resource'] = source_resource
    return render(request, "sources/sources_import.html", args)
