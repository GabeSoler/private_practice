"""Account creation for PPM app"""

from django.shortcuts import render, redirect
from .forms import DeleteAccountForm


def profile_view(request):
    """deals with password and user details"""
    return render(request, 'profile.html')


def delete_account_view(request):
    user = request.user
    if request.method != 'POST':
        form = DeleteAccountForm()
    else:
        form = DeleteAccountForm(data=request.POST)
        if form.is_valid():
            form.save()
            if form.cleaned_data['confirm'] == True:
                user.delete()
                return redirect('between_app:index')
            else:
                messages.warning(request, "Account not deleted! Extra confirmation required")
    context = {'form': form}
    return render(request, 'profile/delete.html', context)
