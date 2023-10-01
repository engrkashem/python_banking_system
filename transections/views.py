from typing import Any
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.http import HttpRequest, HttpResponse
from django.views.generic import CreateView, ListView
from transections.constants import DEPOSIT, WITHDRAWAL, LOAN, LOAN_PAID
from datetime import datetime
from django.db.models import Sum
from transections.forms import DepositForm, WithdrawForm, LoanRequestForm, TransectionDateRangeForm
from transections.models import TransectionModel

# Create your views here.


class TransectionReportView(LoginRequiredMixin, ListView):
    template_name = 'transections/transection_report.html'
    model = TransectionModel
    form_data = {}
    balance = 0

    # def get(self, request, *args, **kwargs):
    #     form = TransectionDateRangeForm(request.GET or None)
    #     if form.is_valid():
    #         self.form_data = form.cleaned_data
    #     return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            queryset = queryset.filter(
                timestamp__date__gte=start_date,
                timestamp__date__lte=end_date
            )
            self.balance = TransectionModel.objects.filter(
                timestamp__date__gte=start_date,
                timestamp__date__lte=end_date
            ).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # temp = self.request.user.account.balance
        # if self.start:
        #     self.request.user.account.balance = self.balance
        context.update({
            'account': self.request.user.account,
            'form': TransectionDateRangeForm(self.request.GET or None)
        })

        return context


class TransectionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transections/transection_form.html'
    model = TransectionModel
    title = ''
    success_url = reverse_lazy('transections:transection_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title
        })
        return context


class DepositMoneyView(TransectionCreateMixin):
    form_class = DepositForm
    title = 'Deposit'

    def get_initial(self):
        initial = {'transection_type': DEPOSIT}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        if not account.initial_deposit_date:
            now = timezone.now()
            account.initial_deposit_date = now
        account.balance += amount
        account.save(
            update_fields=[
                'initial_deposit_date',
                'balance'
            ]
        )
        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))} $ was deposited to your account.'
        )
        return super().form_valid(form)


class WithdrawMoneyView(TransectionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw Money'

    def get_initial(self):
        initial = {'transection_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')

        self.request.user.account.balance -= form.cleaned_data.get('amount')
        self.request.user.account.save(update_fields=['balance'])

        messages.success(
            self.request,
            f'Your Withdraw request of {"{:,.2f}".format(float(amount))}$ success'
        )
        return super().form_valid(form)


class LoanRequestView(TransectionCreateMixin):
    form_class = LoanRequestForm
    title = 'Request for Loan'

    def get_initial(self):
        initial = {'transection_type': LOAN}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        current_loan_count = TransectionModel.objects.filter(
            account=self.request.user.account,
            transection_type=3,
            loan_approved=True
        ).count()
        if current_loan_count >= 3:
            return HttpResponse('You have crossed loan limits.')

        messages.success(
            self.request,
            f'Loan request for {"{:,.2f}".format(float(amount))}$ submitted successfully'
        )
        return super().form_valid(form)


class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(TransectionModel, id=loan_id)
        print(loan)
        if loan.loan_approved:
            user_account = loan.account
            # Reduce loan amount from balance
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transection = user_account.balance
                user_account.save()
                loan.loan_approved = True
                loan.transection_type = LOAN_PAID
                loan.save()
                return redirect('transections:loan_list')
            else:
                messages.error(
                    self.request,
                    f'Insuffient balance. You can not pay loan.'
                )
                return redirect('transections:loan_list')


class LoanListView(LoginRequiredMixin, ListView):
    model = TransectionModel
    template_name = 'transections/loan_request.html'
    context_object_name = 'loan'

    def get_queryset(self):
        user_account = self.request.user.account
        queryset = TransectionModel.objects.filter(
            account=user_account,
            transection_type=3
        )
        print(queryset)
        return queryset
