from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.views import *
from django.contrib.auth.forms import PasswordResetForm
import json

from dpia.views import *
from dpia.forms import *
from dpia.models import *


'''
+ start accounts testing
'''

class RegistrationTests(TestCase):
    def setUp(self):
        url = reverse('register')
        self.response = self.client.get(url)

    # check if the status code of the response url is 200 (success!)
    def test_register_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    # check if the name of the reverse-fuction of the url is the correct
    def test_register_url_resolves_register_view(self):
        view = resolve('/register/')
        self.assertEqual(view.func, register)

    # check if the response contains the csrf token
    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    # check if the response form corresponds to the register-forms
    def test_registration_page_contains_form(self):
        user_form = self.response.context.get('user_form')
        profile_form = self.response.context.get('profile_form')
        self.assertIsInstance(user_form, UserForm)
        self.assertIsInstance(profile_form, ProfileForm)

    def test_registration_form_inputs(self):
        '''
        The view must contain 8 inputs: csrf, first_name, last_name, username, email,
        password1, password2 and expertize.
        '''
        self.assertContains(self.response, '<input', 8)
        self.assertContains(self.response, 'type="text"', 4)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="password"', 2)

    def test_registration_form_has_fields(self):
        user_form = UserForm()
        profile_form = ProfileForm()
        expected_user_form = ['first_name', 'last_name', 'username', 'email', 'password', 'password_confirm',]
        expected_profile_form = ['expertise']
        actual_user_form = list(user_form.fields)
        actual_profile_form = list(profile_form.fields)
        self.assertSequenceEqual(expected_user_form, actual_user_form)
        self.assertSequenceEqual(expected_profile_form, actual_profile_form)


## AUTHENTICATION
class SuccessfulRegistrationTests(TestCase):
    def setUp(self):
        self.register_url = reverse('register')
        data = {
            'first_name': 'a',
            'last_name': 'b',
            'username': 'a',
            'email': 'test@gmail.com',
            'password': 'admin123123',
            'password_confirm': 'admin123123',
            'expertise': 'dev'
        }
        self.response = self.client.post(self.register_url, data, follow=True)

        self.login_url = reverse('login')
        self.dashboard_url = reverse('dashboard')


    def test_valid_registration_redirection(self):
        '''
        A valid form submission should redirect the user to the home page
        '''
        self.assertRedirects(self.response, self.login_url)

    def test_user_creation(self):
        '''
        The new user should have been created.
        '''
        self.assertTrue(User.objects.exists())

    def test_login_page_status_code(self):
        '''
        Check if the the user is redirected successfully to the login page.
        '''
        self.login_page = self.client.get(self.login_url)
        self.assertEqual(self.login_page.status_code, 200)


    def test_valid_user_registration_form(self):
        # first submit form with no data
        user_data = {
            'first_name': '',
            'last_name': '',
            'username': '',
            'email': '',
            'password': '',
            'password_confirm': '',
        }
        profile_data = {
         'expertise': '',
        }
        user_form = UserForm(data=user_data)
        profile_form = ProfileForm(data=profile_data)
        # all the form fields should raise 'required' errors.
        self.assertEqual(user_form.errors, {
            'username': ['This field is required.'],
            'email': ['This field is required.'],
            'password': ['This field is required.'],
            'password_confirm': ['This field is required.'],
        })
        self.assertEqual(profile_form.errors, {
            'expertise': ['This field is required.'],
        })

        ## Try again the form submission but now with data
        # get user
        self.user = User.objects.get(username="a")
        user_data = {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'username': 'tester',
            'email': 'test23@gmail.com',
            'password': 'admin123123',
            'password_confirm': 'admin123123',
        }
        profile_data = {
         'expertise': self.user.profile.expertise,
        }
        # fill out the registration forms with the above data
        user_form = UserForm(data=user_data)
        profile_form = ProfileForm(data=profile_data)
        # the user_form and profile_form should be valid with this data
        self.assertTrue(user_form.is_valid())
        self.assertTrue(profile_form.is_valid())



    def test_valid_login_with_username(self):
        # get user
        self.user = User.objects.get(username="a")
        # check if the user profile field is correct
        self.assertEqual(self.user.profile.expertise, 'dev')
        self.assertTrue(self.user.is_active)

        # login the created user
        self.credentials = {
            'username': self.user.username,
            'password': 'admin123123' # we are posting it from the url. the password is save in hash. that's why we cannot do: 'password': self.user.password;
        }
        self.response2 = self.client.post(self.login_url, self.credentials, follow=True)
        # after successful login, the user should redirect to dashboard
        self.assertRedirects(self.response2, self.dashboard_url)
        # the dashboard page opens successfully
        self.assertEqual(self.response2.status_code, 200)
        # check if user in the reponse context is authenticated
        self.auth_user = self.response2.context.get('user')
        self.assertTrue(self.auth_user.is_authenticated)

    def test_valid_login_with_email(self):
        self.response3 = self.client.post(self.login_url, {'username': 'test@gmail.com', 'password': 'admin123123'}, follow=True)
        # the login should be successful, and redirect again to dashboard page.
        self.assertRedirects(self.response3, self.dashboard_url)



class UnsuccessfulRegistrationTests(SuccessfulRegistrationTests):

    def test_invalid_user_registration_form(self):
            # get user
            self.user = User.objects.get(username="a")
            self.assertEqual(self.user.email, 'test@gmail.com')
            # create another set of registration data
            # with !unique username, and unmatching passwords.
            user_data = {
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'username': self.user.username,
                'email': self.user.email,
                'password': 'admin123123',
                'password_confirm': 'admin12312',
            }
            profile_data = {
             'expertise': '', # leave expertise empty.
            }
            # fill out the registration forms with the new data
            user_form = UserForm(data=user_data)
            profile_form = ProfileForm(data=profile_data)
            # the user_form should now raise username and email uniqueness, and password unmatching errors.
            self.assertEqual(user_form.errors, {
                'username': [u'A user with that username already exists.'],
                'email': [u'Email already exists in the database.'],
                'password': [u"Passwords don't match."],
                'password_confirm': [u"Passwords don't match."],
            })
            # the profile_form field should also raise 'required field' error.
            self.assertEquals(profile_form.errors['expertise'], [u"This field is required."])

    def test_invalid_user_login(self):
        # with empty fields
        self.response4 = self.client.post(self.login_url, {'username': '', 'password': ''}, follow=True)
        # the login should fail, and redirect again to login page.
        self.assertRedirects(self.response4, self.login_url)




class ProfileTests(TestCase):
    def setUp(self):
        self.profile_url = reverse('profile')
        self.login_url = reverse('login')

    def test_redirection(self):
        # get the profile page
        response = self.client.get(self.profile_url, follow=True)
        # because of login_required decorator, it should redirect to the login page + the next **kwargs.
        self.assertRedirects(response, '%s?next=%s' %(self.login_url, self.profile_url))

    def test_page_contents(self):
        # first create user
        user = User.objects.create_user(username='max', email="max@gmail.com", password="maxmax1")
        # then login
        self.client.login(username='max', password='maxmax1')
        response = self.client.get(self.profile_url, follow=True)
        self.assertEqual(response.resolver_match.func, profile)
        # profile page content should contain the user object
        self.assertTrue('user' in response.context)


class PasswordChangeTestCase(TestCase):
    '''
    Base test case for form processing
    accepts a `data` dict to POST to the view.
    '''
    def setUp(self):
        self.data = {
            'old_password': 'old_password',
            'new_password1': 'new_password',
            'new_password2': 'new_password',
        }
        self.user = User.objects.create_user(username='john', email='john@doe.com', password='old_password')
        self.url = reverse('password_change')
        self.client.login(username='john', password='old_password')
        self.response = self.client.post(self.url, self.data)


class SuccessfulPasswordChangeTests(PasswordChangeTestCase):
    def test_redirection(self):
        '''
        A valid form submission should redirect the user
        '''
        self.assertRedirects(self.response, reverse('profile'))

    def test_password_changed(self):
        '''
        refresh the user instance from database to get the new password
        hash updated by the change password view.
        '''
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new_password'))

    def test_user_authentication(self):
        '''
        Create a new request to an arbitrary page.
        The resulting response should now have an `user` to its context, after a successful sign up.
        '''
        response = self.client.get(reverse('dashboard'))
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)



class ProfileTestCase(TestCase):
    def setUp(self):
        self.new_user_data = {
            'first_name': 'new_john',
            'last_name': 'new_doe',
            'username': 'new_john',
            'email': 'new_john@doe.com',
            'expertise': 'new_expertise'
        }
        self.user = User.objects.create_user(username='john', email='john@doe.com', password='password1')
        self.url = reverse('profile_edit')
        self.client.login(username='john', password='password1')

class UserProfileCreationTests(ProfileTestCase):
    def test_form_fields(self):
        # get profile_edit page
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # get form
        user_form = response.context.get('user_form')
        profile_form = response.context.get('profile_form')
        # the user-form should have 4 fields.
        self.assertEqual(len(user_form.fields), 4)
        # the profile-form should have 1 field.
        self.assertEqual(len(profile_form.fields), 1)

    def test_user_fields(self):
        # the created user has no first_name, last_name, and no profile-expertise.
        self.assertFalse(self.user.first_name)
        self.assertFalse(self.user.last_name)
        self.assertTrue(self.user.profile)
        self.assertEquals(self.user.user_profile.expertise, '')
        # edit profile expertise
        self.user.user_profile.expertise = "dev"
        self.user.user_profile.save()
        self.assertNotEquals(self.user.user_profile.expertise, '')

    def test_profile_of_user(self):
        profile_id = self.user.profile.id
        profile_obj = UserProfile.objects.get(id=profile_id)
        self.assertEqual(self.user, profile_obj.user)
        self.assertEqual(profile_obj.expertise, '')


class SuccessfulProfileUpdateTests(ProfileTestCase):
    def test_data_after_form_submission(self):
        # submit the new data
        response = self.client.post(self.url, self.new_user_data)
        # check the redirection the the profile-info page
        self.assertRedirects(response, reverse('profile'))
        # go to profile page
        response_2 = self.client.get(reverse('profile'))
        # get the user template context
        user = response_2.context.get('user')
        # check the new data of the user
        self.assertTrue(user.user_profile.expertise, 'new_expertise')
        self.assertTrue(user.username, 'new_john')

    def test_regular_form_submission(self):
        user_form = UserUpdateForm(data={
                                'first_name': 'new_john',
                                'last_name': 'new_doe',
                                'username': 'new_john',
                                'email': 'new_john@doe.com',
                            })
        profile_form = ProfileForm(data={
                                'expertise': 'new_expertise'
                            })

        # the user_form and profile_form should be valid with this data
        self.assertTrue(user_form.is_valid())
        self.assertTrue(profile_form.is_valid())



class InvalidProfileUpdateTests(ProfileTestCase):
    def test_empty_fields(self):
        user_form = UserUpdateForm(data={
                                'first_name': '',
                                'last_name': '',
                                'username': '',
                                'email': '',
                            })
        profile_form = ProfileForm(data={
                                'expertise': ''
                            })

        # the user_form and profile_form should be valid with this data
        self.assertFalse(user_form.is_valid())
        self.assertFalse(profile_form.is_valid())
        # all the form fields should raise 'required' errors.
        self.assertEqual(user_form.errors, {
            'first_name': ['This field is required.'],
            'last_name': ['This field is required.'],
            'username': ['This field is required.'],
            'email': ['This field is required.'],
        })
        self.assertEqual(profile_form.errors, {
            'expertise': ['This field is required.'],
        })

'''
- end accounts testing
'''


'''
+ start questionnaire testing
'''

class PreAssessmentTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='a', email='a@gmail.com', password='password1')
        self.client.login(username='a', password='password1')
        self.url = reverse('pre_assessment')
        # create question objects
        self.question_1 = Question.objects.create(content="How are you?")
        self.question_2 = Question.objects.create(content="Where are you?")
        # create answer objects per each question
        self.answer_1 = self.question_1.create_answer(self.user)
        self.answer_2 = self.question_2.create_answer(self.user)
        self.AnswerFormset = modelformset_factory(Answer, form=AnswerForm, extra=0)

class FormsetTests(PreAssessmentTestCase):

    def test_valid_redirection(self):
        response = self.client.get(self.url)
        # check if the response is valid
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func, pre_assessment)
        # check the context of the pre-assessment template
        self.assertTrue('answer_formset' in response.context)

    def test_valid_question_instance(self):
        q_1 = Question.objects.get(content='How are you?')
        self.assertEqual(self.question_1.id, q_1.id)
        self.assertIsInstance(q_1, Question)

    def test_valid_answer_instance(self):
        response = self.client.get(self.url)
        a_1 = Answer.objects.get(question__content="How are you?")
        a_2 = Answer.objects.get(question__content="Where are you?")
        # check if the new answer objects are instances of the Answer model;
        # and if the foreign-key of the question is equal to the question objects.
        self.assertIsInstance(a_1, Answer)
        self.assertEqual(a_1.question, self.question_1)
        self.assertIsInstance(a_2, Answer)
        self.assertEqual(a_2.question, self.question_2)
        # check if the answers are not assigned to a questionnaire yet.
        self.assertFalse(a_1.questionaire)
        self.assertFalse(a_2.questionaire)
        # check the users assigned to them
        self.assertTrue(a_1.user, self.user)
        # check the length of the formset, i.e. how many instances it contains; it should contain 2 instances.
        self.assertEqual(len(response.context[-1]['answer_formset']), 2)

    # check form
    def form_data(self, answer):
        data = {
                'form-TOTAL_FORMS': 1,
                'form-INITIAL_FORMS': 0,
                'form-0-answer': answer,
            }
        return AnswerForm(data=data)

    def test_valid_form(self):
        form = self.form_data(True)
        self.assertTrue(form.is_valid())

    def test_empty_fields(self):
        """
        Test validation passes when no data is provided
        (data is not required).
        """
        form = self.form_data('')
        self.assertTrue(form.is_valid())
        # the form should have 1 field.
        self.assertEqual(len(form.fields), 1)


    # test formset
    def test_empty_formset(self):
        formset = self.AnswerFormset({
            'form-INITIAL_FORMS': '0',
            'form-TOTAL_FORMS': '2',
            'form-0-answer': None,
            'form-1-answer': None,
        })
        # it should raise no errors, since the default boolean answer is False.
        self.assertTrue(formset.is_valid())


    def test_valid_formset(self):
        data = {
                'answer_formset-TOTAL_FORMS': 2,
                'answer_formset-INITIAL_FORMS': 0,
                'answer_formset-0-answer': True,
                'answer_formset-1-answer': True,
            }

        answer_queryset = Answer.objects.all()
        answer_formset = self.AnswerFormset(data=data, queryset=answer_queryset, prefix='answer_formset')
        # the queryset should contain two answer objects.
        self.assertEqual(len(answer_queryset), 2)
        self.assertEqual(answer_formset.prefix, 'answer_formset')
        # the reponse context formset should have the same length as the defined formset.
        response = self.client.get(self.url)
        self.assertEqual(len(response.context[-1]['answer_formset']), len(answer_formset))
        # each answer object should have no questionnaire; and a user!
        for answer in answer_queryset:
            self.assertFalse(answer.questionaire)
            self.assertEqual(answer.user, self.user)
            self.assertEqual(answer.answer, False)
        # each answer form field should be True, since the data we submitted through the formset is True!
        for form in answer_formset:
            self.assertEqual(form.instance.questionaire, answer_queryset[0].questionaire)
            self.assertEqual(form['answer'].data, True)

'''
- end pre-assessment testing
'''

'''
+ start questionnaire testing
'''

class QuestionaireSetUp(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='a', email='a@gmail.com', password='password1')
        self.client.login(username='a', password='password1')
        self.url = reverse('q_add')

class PreAssessmentRequiredDecoratorTests(QuestionaireSetUp):
    def setUp(self):
        # get the attributed defined in the LoginCredentials setUp.
        super(PreAssessmentRequiredDecoratorTests, self).setUp()

    def test_invalid_redirection(self):
        response = self.client.get(self.url)
        pre_assessment_url = reverse('pre_assessment')
        # it should redirect to pre-assessment
        self.assertEqual(response.status_code, 302) #302 is the redirection status_code.
        self.assertRedirects(response, pre_assessment_url)

    def test_valid_redirection(self):
        # create question object
        question_1 = Question.objects.create(content="How are you?")
        # create answer object per each question
        answer_1 = question_1.create_answer(self.user)
        response = self.client.get(self.url)
        # now it should redirect to q_add page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func, q_add)
        # check if the response context contains the 'questionaire-form'
        self.assertTrue('q_form' in response.context)


class QuestionaireFormTests(QuestionaireSetUp):
    def setUp(self):
        super(QuestionaireFormTests, self).setUp()
        # create question object
        self.question_1 = Question.objects.create(content="How are you?")
        # create answer object per each question
        self.answer_1 = self.question_1.create_answer(self.user)
        self.response = self.client.get(self.url)

    def test_form_fields(self):
        # get form from the response context
        q_form = self.response.context.get('q_form')
        # the q-form should have 2 fields.
        self.assertEqual(len(q_form.fields), 2)


    def test_valid_form(self):
        data = {
            'description': 'test questionnaire 2',
            'aim_of_dpia': 'testing_2'
        }
        q_form = QuestionaireForm(data=data)
        self.assertTrue(q_form.is_valid())

    def test_invalid_form(self):
        data = {
            'description': '', # this field should normally not be empty.
            'aim_of_dpia': '' # this field can also be empty.
        }
        q_form = QuestionaireForm(data=data)
        self.assertFalse(q_form.is_valid())
        self.assertEqual(q_form.errors, {'description': ['This field is required.']})



    def test_valid_post_data(self):
        data = {
            'description': 'test questionnaire',
            'aim_of_dpia': 'testing'
        }
        # post data
        resp = self.client.post(self.url, data, follow=True)
        # successful data submission should redirect to the dashboard
        self.assertRedirects(resp, reverse('dashboard'))
        # check the newly created questionnaire, it's member and the assigned pre-assessment.
        q = Questionaire.objects.all()[0]
        self.assertEqual(q.aim_of_dpia, 'testing')
        self.assertEqual(len(q.members.all()), 1)
        self.assertTrue(self.user in q.members.all())
        self.assertTrue(Answer.objects.filter(questionaire=q).exists())
        # check the response context
        get_resp = self.client.get(reverse('dashboard'))
        self.assertTrue('user_memberships' in get_resp.context)
        #self.assertTrue('deleted_questionnaires' in get_resp.context)
        self.assertEqual(len(get_resp.context[-1]['user_memberships']), 1)
        #self.assertEqual(len(get_resp.context[-1]['deleted_questionnaires']), 0)
        # test memberships of the created questionnaire
        memberships = get_resp.context.get('user_memberships')
        self.assertEqual(len(memberships), 1)
        for membership in memberships:
            # the member associated with the q-creation should be the current user;
            self.assertEqual(membership.member, self.user)
            # and also the owner of the questionnaire.
            self.assertTrue(membership.is_owner)


    def test_invalid_post_data(self):
        data = {
            'description': '',
            'aim_of_dpia': 'testing'
        }

        # post data
        resp = self.client.post(self.url, data, follow=True)
        # # the invalid post should redirect again to the same page.
        # self.assertRedirects(respo, reverse('q_add'))
        # check response url and func
        self.assertEqual(resp.resolver_match.func, q_add)
        # get form from the response context
        form = resp.context.get('q_form')
        # the form should be a QuestionaireForm instance
        self.assertIsInstance(form, QuestionaireForm)
        # the form should have raised errors.
        self.assertEqual(form.errors, {'description': ['This field is required.']})
        # check if there are created any questionnaires.
        # the quyerset number should be 0!
        Qs = Questionaire.objects.all()
        self.assertEqual(len(Qs), 0)
        # the same for the memberships.
        memberships = Membership.objects.all()
        self.assertEqual(len(memberships), 0)
        # and for the pre-assessment answers.
        answers = Answer.objects.filter(questionaire__isnull=False) # the filter checks only for the answers assigned to a q.
        self.assertEqual(len(answers), 0)


class QuestionaireCRUDTests(QuestionaireSetUp):
    # CRUD: Create Read Update Delete
    # Create tests are done in the step above (QuestionaireFormTests)
    def setUp(self):
        super(QuestionaireCRUDTests, self).setUp()
        self.q = Questionaire.objects.create(description='testing', aim_of_dpia='testing')
        self.membership = Membership.objects.create(questionaire=self.q, member=self.user, is_owner=True)
        self.dashboard = reverse('dashboard')
        self.response = self.client.get(self.dashboard)
        # create another user
        self.user_2 = User.objects.create_user(username='dummy', email='dummy@gmail.com', password='password2')

class QuestionaireReadTests(QuestionaireCRUDTests):
    def setUp(self):
        super(QuestionaireReadTests, self).setUp()

    # Read tests
    def test_redirection(self):
        self.assertEqual(self.response.status_code, 200)

    def test_response_context(self):
        # check length of the queryset
        self.assertEqual(len(self.response.context['user_memberships']), 1)
        # check username of the member.
        self.assertEqual([membership.member.username for membership in self.response.context['user_memberships']], ['a'])
        # check questionnaire of the membership.
        self.assertEqual([membership.questionaire for membership in self.response.context['user_memberships']], [self.q])

    def test_valid_access(self):
        members = reverse('members', args=[self.q.id])
        response = self.client.get(members)
        self.assertEqual(response.status_code, 200)


    # def test_invalid_access(self):
    #     # log out current user
    #     self.client.logout()
    #     # login the new user.
    #     self.client.login(username='a', password='password2')
    #     # check context of the dashboard. It should be empty.
    #     response = self.client.get(self.dashboard)
    #     self.assertEqual(len(response.context['user_memberships']), 0)
    #     # now try to access the questionaire (member's page, for example) of the other user, of which this current user is not a member (should have no access to!).
    #     members = reverse('members', args=[self.q.id])
    #     response = self.client.get(members)
    #     # the response should raise a 404 Not Found error.
    #     self.assertEqual(response.status_code, 404)
    #     # redirect the user to the dashboard
    #     response_dashboard = self.client.get(self.dashboard)
    #     # the questionaire table should be empty.
    #     self.assertTrue('You are not assigned to any DPIA questionnaire yet.' in response_dashboard.content)
    #     # check the username of the user in the response content
    #     self.assertTrue(self.user_2.username in response_dashboard.content)


class QuestionaireUpdateTests(QuestionaireCRUDTests):
    def setUp(self):
        super(QuestionaireUpdateTests, self).setUp()
        # add another member (non-owner!) to the questionnaire.
        new_member = Membership.objects.create(questionaire=self.q, member=self.user_2, is_owner=False)

    def test_pre_assessment_update(self):
        # check if the user is at the dashboard page
        self.assertEqual(self.response.status_code, 200)
        # for this particular test, the user should have no pre-assessment assigned
        answers = Answer.objects.filter(user=self.user).exists()
        self.assertFalse(answers)
        # the questionnaire shouldn't either; normally they have!
        answers = Answer.objects.filter(questionaire=self.q).exists()
        self.assertFalse(answers)
        # redirect to pre-assessment update page
        response = self.client.get(reverse('pre_assessment_update', args=[self.q.id]))
        # check content
        self.assertTrue('Update Pre-Assessment' in response.content)
        # check context; it should contain no pre-assessment
        self.assertEqual(len(response.context['answer_formset']), 0)

    # def test_valid_questionaire_update(self):
    #     update_q_url = reverse('q_edit', args=[self.q.id])
    #     response = self.client.post(update_q_url, data={'description': 'updated description', 'aim_of_dpia': 'updated aim'})
    #     self.assertEqual(response.status_code, 200)
    #     response_dict = response.json()
    #     print response_dict['html_form']
        # self.assertJSONEqual(json_response.value, 'updated description')
        # print response.json()['user_memberships']
        # the questionnaire details should have changed now
        # self.assertEqual(self.q.description, 'updated description')
        # dashboard_response = self.client.get(self.dashboard)
        # self.assertEqual(dashboard_response.context['user_memberships'][0].questionaire.description, 'updated description')

    # def test_invalid_questionaire_update(self):
        # pass






'''
- end questionnaire testing
'''



# # import unittest
# # from django.test import TestCase
# # from django.test import Client
# # from django.contrib.staticfiles.testing import StaticLiveServerTestCase
# #
# # from selenium.webdriver.firefox.webdriver import WebDriver
# # from selenium.webdriver.support.wait import WebDriverWait
# # from selenium.webdriver.common.keys import Keys
# # from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.common.keys import Keys
# # from selenium.webdriver.support.ui import Select
# # from selenium.common.exceptions import NoSuchElementException
# # from selenium.common.exceptions import NoAlertPresentException
# # import unittest, time, re
# #
# # from django.urls import reverse
# # from django.contrib import auth
# # from django.contrib.auth import get_user_model
# #
# # from .models import *
# # from .forms import *
# # from .views import *
# # # Create your tests here.
# #
# # ### Selenium Tests
# # # class MySeleniumTests(StaticLiveServerTestCase):
# # #
# # #     @classmethod
# # #     def setUpClass(cls):
# # #         super(MySeleniumTests, cls).setUpClass()
# # #         binary = FirefoxBinary(r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe')
# # #         cls.selenium = WebDriver(firefox_binary=binary)
# # #         cls.selenium.implicitly_wait(10)
# # #
# # #     @classmethod
# # #     def tearDownClass(cls):
# # #         cls.selenium.quit()
# # #         super(MySeleniumTests, cls).tearDownClass()
# # #
# # #     def test_login(self):
# # #         timeout = 2
# # #         self.selenium.get('%s%s' % (self.live_server_url, '/'))
# # #         username_input = self.selenium.find_element_by_name("username")
# # #         username_input.send_keys('admin')
# # #         password_input = self.selenium.find_element_by_name("password")
# # #         password_input.send_keys('admin')
# # #         self.selenium.find_element_by_name("login").click()
# # #         # Wait until the response is received
# # #         WebDriverWait(self.selenium, timeout).until(
# # #             lambda driver: driver.find_element_by_tag_name('body'))
# # #
# # #         self.selenium.find_element_by_link_text("Nobel Grid Carbon Co-op Use Cases").click()
# # #         self.selenium.find_element_by_xpath("(//button[@type='button'])[9]").click()
# # #         self.selenium.find_element_by_xpath("(//a[contains(text(),'Edit')])[9]").click()
# # #         self.selenium.find_element_by_css_selector("button.btn.btn-primary").click()
# # #         self.selenium.find_element_by_link_text("Logout").click()
# #
# #
# # ## Unit tests
# # class ViewsTest(TestCase):
# #         # def test_login(self):
# #         #     # Issue a GET request.
# #         #     response = self.client.post('/', {'username': 'admin', 'password': 'admin'})
# #         #     # Check that the response is 200 OK.
# #         #     self.assertEqual(response.status_code, 200)
# #         #     # Verify the view that served the response
# #         #     self.assertEqual(response.resolver_match.func, user_login)
# #         #
# #         # def test_home(self):
# #         #     # Issue a GET request.
# #         #     response = self.client.get(reverse('home'))
# #         #     # Check that the response is 302 OK.
# #         #     self.assertEqual(response.status_code, 302)
# #         #     # Verify the view that served the response
# #         #     self.assertEqual(response.resolver_match.func, home)
# #         #
# #         # def test_unauthorized_login_at_home(self):
# #         #     response = self.client.get(reverse('login'))
# #         #     self.assertIsNotNone(response.context)
# #
# #     def setUp(self):
# #         self.client = Client()
# #         ## create new user
# #         new_user = User.objects.create(first_name="a", last_name="b", username="django_tester", password="test", email="a@gmai.com", is_active=False)
# #         ## create new user-profile
# #         new_userprofile = UserProfile.objects.create(user=new_user, expertise="Tester")
# #         ## create new Questionnaire
# #         new_q = Questionaire.objects.create(description="TestCase", aim_of_dpia="TestCaseAim")
# #         ## create membership
# #         new_membership = Membership.objects.create(member=new_userprofile, questionaire=new_q, owner=True, responsibility_in_dpia="tester")
# #         ## add new source
# #         new_source = SourceInventory.objects.create(questionaire=new_q, name="Source_test")
# #
# #     def test_user_creation(self):
# #
# #         get_user = User.objects.get(first_name="a")
# #         get_userprofile = UserProfile.objects.get(user__username="django_tester")
# #         ## check if the created user-profile is related to the created user
# #         self.assertEqual(str(get_userprofile.expertise), str(get_user.userprofile.expertise))
# #         ## check if user-profile is not activated
# #         self.assertFalse(get_userprofile.user.is_active)
# #         # check username of the user through userprofile
# #         self.assertEqual(str(get_userprofile.__unicode__()), str(get_user.username))
# #
# #
# #     def test_questionnaire_membership(self):
# #         get_user = User.objects.get(first_name="a")
# #         get_userprofile = UserProfile.objects.get(user__username="django_tester")
# #         get_membership = Membership.objects.get(responsibility_in_dpia="tester")
# #         # Check if the username of the user is the same as the username of the userprofile related to the membership of that questionnaire
# #         self.assertEqual(get_user.username, get_membership.member.user.username)
# #         # Check if the user related to the questionnaire is active
# #         self.assertFalse(get_membership.member.user.is_active)
# #         # activate the user through the membership
# #         get_membership.member.user.is_active = True
# #         # save it
# #         get_membership.save()
# #         # Check if the user related to the questionnaire is active
# #         self.assertTrue(get_membership.member.user.is_active)
# #
# #     def test_source_creation(self):
# #         get_source = SourceInventory.objects.get(name="Source_test")
# #         self.assertEqual(str(get_source), 'Source_test')
