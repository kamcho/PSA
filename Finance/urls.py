from django.urls import path

from . import views
from .views import *
urlpatterns = [

    path('', FinanceHome.as_view(), name='finance'),
    path('CreateInvoice/', CreateInvoice.as_view(), name='create-invoice'),
    path('Invoices/', InvoicesListView.as_view(), name='invoices'),
    path('Invoices/<str:id>/', InvoiceDetail.as_view(), name='invoice-id'),
    path('SalariesDisbursment/', Salarypayment.as_view(), name='salary-payment'),
    path('ConfirmSalaryPayment/', ConfirmSalaryPayments.as_view(), name='confirm-payment'),
    path('InvoicePayments/', InvoiceDisbursments.as_view(), name='invoice-payments'), # type: ignore
    path('InvoicePayments/<str:id>/', InvoicePaymentId.as_view(), name='invoice-payment-id'),
    path('Transactions/', TransactionsHome.as_view(), name='transactions'),
    path('InitiatedPayments/', InitiatedTransactions.as_view(), name='initiated-payments'),
    path('ProcessedPayments/', ProcessedTransactions.as_view(), name='processed-payments'),
    path('SuccesfulPayments/', SuccesfulPayouts.as_view(), name='succesful-payouts'),
    path('InitiatedPayments/<str:receipt>/Receipt/', views.initiated_payment_receipt, name='initiated-receipt'),
    path('ProcessedPayments/<str:receipt>/Receipt/', views.processed_payment_receipt, name='processed-receipt'),
    path('SuccessfulPayouts/<str:receipt>/Receipt/', views.payout_receipt, name='payout-receipt'), # type: ignore
    path('CreateTerm/', CreateTerm.as_view(), name='create-term'),
    path('FeesListView/', FeesListView.as_view(), name='fees-list'),
    path('SetFees/', SetFees.as_view(), name='set-fees'),
    path('ManageFees/<str:id>/', ManageFees.as_view(), name='manage-fees'),
    path('FeePaymentTransactions/', SchoolFeeTransactions.as_view(), name='fee-transactions'),
    path('ProcessedFeePayments/', ProcessedFeePayments.as_view(), name='processed-fee-payments'),
    path('SchoolFeesManagement/', FeesHome.as_view(), name='fees-home'),
    path('FeePaymentTransactions/<str:id>/', ManageFeeTransaction.as_view(), name='manage-fee-transaction'),
    path('ProcessedFeePayments/<str:id>/', ManageProcessedFeePayment.as_view(), name='manage-fee-payment'),
    path('<str:email>/FeeProfile/', StudentsFeeProfile.as_view(), name='student-fee-profile'),
    path('StudentsFeeBalances/', SchoolFeesBalance.as_view(), name='school-fees-balances'),
    path('<str:class_id>/FeeBalances/', ClassFeeBalances.as_view(),name='class-balances'),




]