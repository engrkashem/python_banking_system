from django.urls import path
from transections.views import DepositMoneyView, WithdrawMoneyView, TransectionReportView, LoanRequestView, LoanListView, PayLoanView

urlpatterns = [
    path('deposit/', DepositMoneyView.as_view(), name='deposit_money'),
    path('report/', TransectionReportView.as_view(), name='transection_report'),
    path('withdraw/', WithdrawMoneyView.as_view(), name='withdraw_money'),
    path('loan_request/', LoanRequestView.as_view(), name='loan_request'),
    path('loans/', LoanListView.as_view(), name='loan_list'),
    path('loans/<int:loan_id>/', PayLoanView.as_view(), name='pay'),
]
