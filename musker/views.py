from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile, Meep
from .forms import (
    MeepForm,
    SignUpForm,
    ProfilePicForm,
    UserProfileUpdateForm,
    ChangePasswordForm,
)


def home(request):
    """Home view: Displays the main page with Meeps and MeepForm."""
    if request.user.is_authenticated:
        form = MeepForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                # Save the Meep associated with the logged-in user
                meep = form.save(commit=False)
                meep.user = request.user
                meep.save()
                messages.success(request, ('Your Meep Has Been Posted!'))
                return redirect('home')

        # Retrieve all Meeps and render the home page
        meeps = Meep.objects.all().order_by('-created_at')
        return render(request, 'home.html', {'meeps': meeps, 'form': form})
    else:
        # If user is not authenticated, display Meeps without the MeepForm
        meeps = Meep.objects.all().order_by('-created_at')
        return render(request, 'home.html', {'meeps': meeps})


def profile_list(request):
    """Profile List view: Displays a list of profiles, excluding the logged-in user."""
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user)
        return render(request, 'profile_list.html', {'profiles': profiles})
    else:
        messages.success(request, ('You must be logged in!'))
        return redirect('home')


def profile(request, pk):
    """Profile view: Displays a user's profile and their Meeps, allows following/unfollowing."""
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        meeps = Meep.objects.filter(user_id=pk)

        # Handle following/unfollowing logic
        if request.method == 'POST':
            current_user_profile = request.user.profile
            action = request.POST['follow']
            if action == 'unfollow':
                current_user_profile.follows.remove(profile)
            elif action == 'follow':
                current_user_profile.follows.add(profile)
            current_user_profile.save()

        return render(request, 'profile.html', {'profile': profile, 'meeps': meeps})
    else:
        messages.success(request, ('You must be logged in !'))
        return redirect('home')


def update_user(request):
    """Update User view: Handles updating user profile information and picture."""
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        profile_user = Profile.objects.get(user__id=request.user.id)
        user_form = UserProfileUpdateForm(request.POST or None, request.FILES or None, instance=current_user)
        profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance=profile_user)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Save updated user and profile information
            user_form.save()
            profile_form.save()
            login(request, current_user)
            messages.success(request, ('Profile has been updated!'))
            return redirect('home')

        return render(request, 'update_user.html', {'user_form': user_form, 'profile_form': profile_form})
    else:
        messages.success(request, ('You must be logged in !'))
        return redirect('home')


def followers(request, pk):
    """Followers view: Displays the followers of a user."""
    if request.user.is_authenticated:
        if request.user.id == pk:
            profiles = Profile.objects.get(user_id=pk)
            return render(request, 'followers.html', {'profiles': profiles})
        else:
            messages.success(request, ("That's not your profile"))
            return redirect('home')
    else:
        messages.success(request, ("You must be logged in !"))
        return redirect('home')


def follows(request, pk):
    """Follows view: Displays the users that the current user is following."""
    if request.user.is_authenticated:
        if request.user.id == pk:
            profiles = Profile.objects.get(user_id=pk)
            return render(request, 'follows.html', {'profiles': profiles})
        else:
            messages.success(request, ("That's not your profile"))
            return redirect('home')
    else:
        messages.success(request, ("You must be logged in !"))
        return redirect('home')


@login_required
def change_password(request):
    """Change Password view: Handles changing the user's password."""
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important for maintaining the user's session
            messages.success(request, ('Your password is changed'))
            return redirect('home')  # Redirect to the profile page after successful password change
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'change_password.html', {'form': form})


def login_user(request):
    """Login view: Handles user authentication and login."""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ('You have been logged in !'))
            return redirect('home')
        else:
            messages.success(request, ('There was an error, try again!'))
            return redirect('login')
    else:
        return render(request, 'login.html')


def logout_user(request):
    """Logout view: Logs out the user."""
    logout(request)
    messages.success(request, ('You have been logged out !'))
    return redirect('home')


def register_user(request):
    """Register User view: Handles user registration."""
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # log in user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ('You have been Registered !'))
            return redirect('home')
    return render(request, 'register.html', {'form': form})


def meep_like(request, pk):
    """Meep Like view: Handles liking/unliking Meeps."""
    if request.user.is_authenticated:
        meep = get_object_or_404(Meep, id=pk)
        if meep.likes.filter(id=request.user.id):
            meep.likes.remove(request.user)
        else:
            meep.likes.add(request.user)
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.success(request, ("You must be logged in!"))
        return redirect('home')


def meep_share(request, pk):
    """Meep Share view: Displays a single Meep for sharing."""
    meep = get_object_or_404(Meep, id=pk)
    if meep:
        return render(request, 'meep_share.html', {'meep': meep})
    else:
        messages.success(request, ("This Meep does not exist"))
        return redirect('home')


def meep_delete(request, pk):
    """Meep Delete view: Handles deleting Meeps."""
    if request.user.is_authenticated:
        meep = get_object_or_404(Meep, id=pk)
        # check if you own the meep
        if request.user.username == meep.user.username:
            # delete it!
            meep.delete()
            messages.success(request, ("The meep deleted!"))
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.success(request, ("You can only remove your own meeps!"))
            return redirect('home')


def meep_edit(request, pk):
    """Meep Edit view: Handles editing Meeps."""
    meep = get_object_or_404(Meep, id=pk)
    if request.user.is_authenticated:
        # check if you own the meep
        if request.user.username == meep.user.username:
            form = MeepForm(request.POST or None, instance=meep)
            if request.method == 'POST':
                if form.is_valid():
                    meep = form.save(commit=False)
                    meep.user = request.user
                    meep.save()
                    messages.success(request, ('Your Meep Has Been Updated!'))
                    return redirect('home')
            else:
                return render(request, "meep_edit.html", {'form': form, 'meep': meep})
        else:
            messages.success(request, ("You can only edit your own meeps!"))
            return redirect('home')
    else:
        messages.success(request, ("You must be logged in!"))
        return redirect('home')


def search(request):
    """Search view: Handles Meep search based on user input."""
    if request.method == 'POST':
        # grab the search input
        search = request.POST['search']
        # search the db
        searched = Meep.objects.filter(body__contains=search)
        return render(request, 'search.html', {'search': search, 'searched': searched})
    else:
        return render(request, 'search.html', {})


def user_search(request):
    """User Search view: Handles user search based on username."""
    if request.method == 'POST':
        # grab the search input
        search = request.POST['user_search']
        # search the db
        searched = User.objects.filter(username__contains=search)
        return render(request, 'user_search.html', {'search': search, 'searched': searched})
    else:
        return render(request, 'user_search.html', {})
