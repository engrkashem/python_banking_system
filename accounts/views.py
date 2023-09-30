from typing import Any
from django import http
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, RedirectView
from .forms import UserAddressForm, UserRegistrationForm

User = get_user_model()

# Create your views here.


class UserRegistrationView(TemplateView):
    model = User
    form_class = UserRegistrationForm
    template_name = ''  # to be filled

    def dispatch(self, request, *args: Any, **kwargs: Any):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect('')  # to be filled
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        registration_form = UserRegistrationForm(self.request.POST)
        address_form = UserAddressForm(self.request.POST)
        if registration_form.is_valid() and address_form.is_valid():
            user = registration_form.save()
            address = address_form.save()
            login(self, request, user)
            messages.success(
                self, request, (f'Thanks for choosing BaperBank. Your account no is {user.account.account_no}'))
            return HttpResponseRedirect(reverse_lazy(''))  # to be filled

        return self.render_to_response(
            self.get_context_data(
                registration_form=registration_form,
                address_form=address_form
            )
        )

    def get_context_data(self, **kwargs: Any):
        if 'registration_form' not in kwargs:
            kwargs['registration_form'] = UserRegistrationForm()
        if 'address_form' not in kwargs:
            kwargs['address_form'] = UserAddressForm()
        return super().get_context_data(**kwargs)


class UserLoginView(LoginView):
    template_name = ''  # tobe filled
    redirect_authenticated_user = False


class UserLogoutView(RedirectView):
    pattern_name = ''  # to be filled whice to redirect

    def get_redirect_url(self, *args: Any, **kwargs: Any):
        if self.request.user.is_authenticated:
            logout(self.request)
        return super().get_redirect_url(*args, **kwargs)
