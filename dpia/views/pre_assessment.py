from dpia.modules import *
from dpia.views.generic_dicts import questions_dict

@login_required
def pre_assessment(request):
    '''
    Shows a formet of pre-assessment questions and answers, based on the first criterion of questions.
    Because the answers cannot yet be assigned to a questionnaire, since the latter will the created in the last step of the pre-assessment, the answers are assigned to the user object and the questionnaire field is left empty. Only after the pre-assessment is finished, are they assigned to the questionnaire created by the user.
    '''

    user = request.user
    questions = Question.objects.prefetch_related('question_in_answer').all()
    # if no questions in the db yet, create them from the dictionary saved in generic_dicts!
    if not questions.exists():
        for question in questions_dict:
            Question.objects.get_or_create(content=question)

    answers = Answer.objects.select_related('question', 'questionaire', 'user').filter(user=user, questionaire=None)

    # create answer objects for the user
    if not answers.exists():
        for question in questions:
            question.create_answer(user)

    # Assess Pre-assessment
    AnswerFormset = modelformset_factory(Answer, form=AnswerForm, extra=0)
    answer_formset = AnswerFormset(request.POST or None, queryset=answers)
    for form in answer_formset:
        form.fields['answer'].label = form.instance.question.content
    if request.POST:
        if answer_formset.is_valid():
            answer_formset.save()
            # messages.info(request, u'Please confirm the pre-assessment.')
            return redirect('pre_assessment_confirmation')
        else:
            messages.error(request, u'Please fill out the fields.')

    args = {}
    args.update(csrf(request))
    args['answer_formset'] = answer_formset
    return render(request, "pre-assessment/questions_list.html", args)


## Assess Pre-Assessment and Create Questionnaire
@login_required
def pre_assessment_confirmation(request):
    '''
    All the questions and their answers are listed, and the user is given the option of confirming the Pre-Assessment or discard it.
    If the user chooses to discard it, the Pre-Assessment is deleted and the user is redirected to the homepage. Otherwise, if the user confirms it, he/she is directed to a new page, where he/she can create the questionnaire.
    '''
    user = request.user
    answers = Answer.objects.select_related('question', 'questionaire', 'user').filter(user=user, questionaire=None).order_by('question')
    if request.POST:
        # If the user says Yes to the DPIA Pre-Assessment
        if 'yes' in request.POST:
            messages.success(request, u'Pre-Assessment was saved successfully.')
            return redirect('q_add')
        # elif 'no' in request.POST:
        #     for answer in answers:
        #         answer.delete()
        #         messages.success(request, u'Pre-assessment was deleted successfully.')
        #         return redirect('dashboard')

    args = {}
    args.update(csrf(request))
    args['answers'] = answers
    return render(request, 'pre-assessment/confirmation.html', args, request)


@login_required
# @transaction.atomic
def pre_assessment_update(request, q_id=None):
    '''
    Updates the answers of the Pre-Assessment. This function is available after the creation of the questionnaire.
    '''
    q = get_object_or_404(Questionaire, q_in_membership__member=request.user, id=q_id)
    answers = Answer.objects.select_related('question', 'questionaire', 'user').filter(questionaire=q).order_by('question')
    AnswerFormset = modelformset_factory(Answer, form=AnswerForm, extra=0)
    answer_formset = AnswerFormset(queryset=answers)
    for form in answer_formset:
        form.fields['answer'].label = form.instance.question.content

    with reversion.create_revision():
        if request.POST:
            answer_formset = AnswerFormset(request.POST)
            if answer_formset.is_valid():
                for form in answer_formset.forms:
                    answer = form.save(commit=False)
                    answer.questionaire = q
                    answer.save()
                # Store some meta-information.
                save_revision_meta(request.user, q, 'Updated pre-assessment of questionnaire "{}".'.format(q.description))
                message = messages.success(request, u'Pre-assessment of questionnaire "%s" was changed successfully.' %(q.description))
                return redirect('members', q.id)
            else:
                messages.error(request, u'Please fill out the fields.')

    args = {}
    args.update(csrf(request))
    args['q'] = q
    args['answer_formset'] = answer_formset
    return render(request, "pre-assessment/update.html", args)
