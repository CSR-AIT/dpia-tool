from dpia.modules import *

# register new users.
def register(request):
    """
    Registers new users.
    """

    if request.user.is_authenticated():
        return redirect('dashboard')
    else:
        user_form = UserForm(request.POST or None)
        profile_form = ProfileForm(request.POST or None)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            # hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()
            # Now sort out the Profile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, "Registration was successful.")# Please wait for the confirmation of your account.")
            return redirect('login')
        else:
            pass
            # messages.error(request, user_form.errors, profile_form.errors)
            # print user_form.errors, profile_form.errors

    args = {}
    args.update(csrf(request))
    args['user_form'] = user_form
    args['profile_form'] = profile_form
    return render(request, 'accounts/register.html', args)



def user_login(request):
    '''
    Logs in user.
    If the users are activated, they are directed to the homepage.
    If not, an error message to wait for the activation is shown.
    If the users are activated but they still cannot login, it means they entered an incorrect username or password.
    '''

    if request.user.is_authenticated():
        return redirect('dashboard')
    else:
        # Get next url
        url_with_get = request.GET.get('next')
        if request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user:
                # Is the account active? It could have been disabled.
                if user.is_active:
                    login(request, user)
                    # if 'next' is empty redirect to home; else redirect to the url saved in the next variable.
                    if url_with_get:
                        return redirect(url_with_get)
                    else:
                        return redirect('dashboard')
                else:
                    # An inactive account was used - no logging in!
                    messages.error(request, "Your DPIA account is disabled. Please wait for the activation.")
                    return HttpResponseRedirect(reverse('login'))
            else:
                if username == "" and password == "":
                    # Empty credentials
                    messages.error(request, "Please enter your credentials.")
                else:
                    messages.error(request, "Incorrect username/email or password.")
                return redirect('login')
        else:
            args = {}
            args.update(csrf(request))
            args['next'] = url_with_get
            return render(request, 'accounts/login.html', args)


@login_required
def user_logout(request):
    '''
    Logs out the user.
    '''
    logout(request)
    return redirect('login')



@login_required
def profile(request):
    '''
    Shows all the detailed information of the user (First name, last name, username, email, expertise).
    '''
    user = request.user

    args = {}
    args.update(csrf(request))
    args['user'] = user
    return render(request, 'accounts/profile.html', args)


@login_required
def profile_edit(request):
    '''
    Edits all the profile information.
    '''

    user_form = UserUpdateForm(request.POST or None, instance=request.user)
    profile_form = ProfileForm(request.POST or None, instance=request.user.profile)

    if user_form.is_valid() and profile_form.is_valid():
        user = user_form.save()
        profile = profile_form.save(commit=False)
        profile.user = user
        profile.save()
        messages.success(request, u'Your profile was updated successfully.')
        return redirect('profile')

    args = {}
    args.update(csrf(request))
    args['profile_form'] = profile_form
    args['user_form'] = user_form
    return render(request, 'accounts/profile_edit.html', args)



@login_required
def password_change(request):
    form = CheckPasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)  # Important!
        messages.success(request, 'Your password was successfully updated.')
        return redirect('profile')

    args = {}
    args.update(csrf(request))
    args['form'] = form
    return render(request, 'accounts/password_settings/password_change.html', args)
