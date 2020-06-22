from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

from django.http import Http404
from .models import Profile, User


def verify(request, uuid):
    try:
        user = Profile.objects.get(verification_uuid=uuid)
    except User.DoesNotExist:
        raise Http404("User does not exist or is already verified")
 
    user.is_verified = True
    user.save()
 
    return redirect(reverse_lazy('index'))


def register(request):
    if request.user.is_authenticated:
        return redirect(reverse_lazy('index'))
        
    if request.method == 'POST':
        print(request.POST)
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт {username} успешно создан! Теперь вы можете войти в систему.')
            return redirect('login_page')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, 
                                request.FILES, 
                                instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Аккаунт был успешно обновлён!')
            return redirect('profile_page')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form':   u_form,
        'p_form':   p_form
    }
    return render(request, 'users/profile.html', context)