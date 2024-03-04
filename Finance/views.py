
import imp
from importlib.metadata import PathDistribution
import logging
from django.db import transaction

import string
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum

import random
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView, ListView
from datetime import datetime, timedelta
from django.contrib import messages

from Finance.models import InitiatedPayments, InvoicePayments, Invoices, MpesaPayouts, ProcessedPayments, StudentFeeMpesaTransaction, StudentFeePayment, TermFeeStructure
from Subscription.views import initiate_b2c_payment
from Term.models import Terms
from Users.models import MyUser, SchoolClass, StudentsFeeAccount, TeacherPaymentProfile
# Create your views here.

logger = logging.getLogger('django')

class FinanceHome(TemplateView):
    template_name = 'Finance/finance_home.html'


class CreateInvoice(TemplateView):
    template_name = 'Finance/create_invoice.html'

    def post(self, *args, **kwargs):
        if self.request.method == 'POST':
            title = self.request.POST.get('title')
            description = self.request.POST.get('description')
            amount = self.request.POST.get('amount')
            user = self.request.POST.get('user')
            contact = self.request.POST.get('phone')
            try:
                invoice = Invoices.objects.create(title=title, description=description,
                                                amount=amount, received_from=user, contact_info=contact)
                messages.success(self.request, f'Invoices for {user} created succesfully')
                
                return redirect('invoice-id', invoice.id)
            

            except Exception:

                messages.error(self.request, 'An error occured try again or contact @support.')
                return redirect(self.request.get_full_path())



class Salarypayment(TemplateView):
    template_name = 'Finance/salary_selection.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        users = TeacherPaymentProfile.objects.all().order_by('-salary')
        context['users'] = users

        return context

    def post(self, *args, **kwargs):
        if self.request.method == 'POST':
            ids = self.request.POST.getlist('selected')
            self.request.session['beneficiaries'] = ids
            messages.success(self.request, f'selected {ids}')

            return redirect('confirm-payment')
        

class ConfirmSalaryPayments(TemplateView):
    template_name = 'Finance/salary_payment_confirm.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        ids = self.request.session.get('beneficiaries')
        users = TeacherPaymentProfile.objects.filter(user__email__in=ids).order_by('-salary')
        context['beneficiaries'] = users
        amount = users.aggregate(amount=Sum('salary'))['amount']
        context['amount'] = amount

        return context



class InvoicesListView(TemplateView):
    template_name = 'Finance/invoices.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            invoices = Invoices.objects.all().order_by('-date')
            context['invoices'] = invoices

        except Exception:
            messages.error(self.request, 'An error occured, contact @support')

        return context
    
class InvoiceDetail(TemplateView):
    template_name = 'Finance/invoice_id.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice_id = self.kwargs['id']
        try:
            invoice = Invoices.objects.get(id=invoice_id)
            payments = InvoicePayments.objects.filter(invoice=invoice).order_by('-date')
            context['payments'] = payments
            context['invoice'] = invoice

        except Invoices.DoesNotExist:
            messages.error(self.request, 'We could not find an invoice with the given id. Do not edit URL')
        except Exception:
            messages.error(self.request, 'System error please contact @support')

        return context
    
    def post(self, *args, **kwargs):
        if self.request.method == 'POST':
            invoice_id = self.kwargs['id']
            amount = self.request.POST.get('amount')
            phone = self.request.POST.get('phone')

            messages.success(self.request, f'Payment of {amount} iniiated succesfully.')
            characters = list(string.ascii_letters + string.digits)
            random.shuffle(characters)
            
            # Take the first 8 characters from the shuffled list
            random_alphanumeric = ''.join(characters[:8])
            try:
                initiated_payment = InitiatedPayments.objects.create(amount=amount, tracking_id=invoice_id,
                                                checkout_id=random_alphanumeric, purpose='Invoice')
                pay = initiate_b2c_payment()
                
                # transaction_callback(random_alphanumeric)
                
                return redirect(self.request.get_full_path())

            except Exception:
                pass

            return redirect(self.request.get_full_path())




@transaction.atomic
def transaction_callback(checkout_id):
    try:
        payment = get_object_or_404(InitiatedPayments, checkout_id=checkout_id)
        processed_payment = ProcessedPayments.objects.create(initiator_id=payment, transaction_id='qwertwweew', status=1)

        if payment.purpose == 'Invoice':

            tracking_no = payment.tracking_id
            amount = payment.amount

            invoice = get_object_or_404(Invoices, id=tracking_no)
            balance = invoice.balance
            new_balance = balance - amount


            invoice_payment = InvoicePayments.objects.create(invoice=invoice, amount=amount, balance=new_balance, cleared=1)

            invoice.balance = new_balance
            invoice.save()

        elif payment.purpose == 'Remedial':
            print('yeees')
            for user in payment.beneficiaries.all():
                try:
                    payouts = MpesaPayouts.objects.create(user=user, checkout_id=processed_payment,
                                                        phone='254783680273', amount=1000, balance=200,
                                                            receipt='ydkshkdkdyjd')
                except Exception as e:
                    print(str(e))

        elif payment.purpose == 'Salary':
            user = 'user'
            payouts = MpesaPayouts.objects.create(user=user, checkout_id=processed_payment,
                                                        phone='254783680273', amount=1000, balance=200,
                                                            receipt='ydkshkdkdyjd')





    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return None




class InvoiceDisbursments(TemplateView):
    template_name = 'Finance/invoice_payments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            payments = InvoicePayments.objects.all().order_by('-date')
            context['payments'] = payments

        except Exception:
            messages.error(self.request, 'System error please contact @support')

        return context

class InvoicePaymentId(TemplateView):
    template_name = 'Finance/invoice_payment_id.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment_id = self.kwargs['id']

        try:
            payment = InvoicePayments.objects.get(id=payment_id)
            context['payment'] = payment
            invoice = Invoices.objects.get(id=payment.invoice.id)
            context['invoice'] = invoice

        except InvoicePayments.DoesNotExist:
            messages.error(self.request, 'We could not find a transaction with the given id')

        except Exception:
            messages.error(self.request, 'System error please contact @support')

        return context


class TransactionsHome(TemplateView):
    template_name = 'Finance/finance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            transactions = MpesaPayouts.objects.all().order_by('-date')
            context['transactions'] = transactions
        except Exception as e:
            messages.error(self.request, 'Database Error ! Contact @Support !!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )


        return context

class InitiatedTransactions(TemplateView):
    template_name = 'Finance/initiated_payments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            transactions = InitiatedPayments.objects.all().order_by('-date')
            context['transactions'] = transactions
        except Exception as e:
            # Handle DatabaseError if needed
            messages.error(self.request, 'An error occurred. We are fixing it!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )


        return context
    
    def post(self, **kwargs):
        if self.request.method == 'POST':
            start_date_str = self.request.POST.get('from')  # Assuming 'from' is the field for start date
            end_date_str = self.request.POST.get('to')
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

            # Add one day to the end date to include transactions on that day
            end_date += timedelta(days=1)
            try:
                # Filter transactions within the date range
                transactions = InitiatedPayments.objects.filter(date__range=[start_date, end_date]).order_by('-date')

                context = {
                    'transactions': transactions
                }
                return render(self.request, self.template_name, context)
            except Exception as e:
                # Handle DatabaseError if needed
                messages.error(self.request, 'An error occurred. We are fixing it!')
                error_message = str(e)  # Get the error message as a string
                error_type = type(e).__name__

                logger.critical(
                    error_message,
                    exc_info=True,  # Include exception info in the log message
                    extra={
                        'app_name': __name__,
                        'url': self.request.get_full_path(),
                        'school': settings.SCHOOL_ID,
                        'error_type': error_type,
                        'user': self.request.user,
                        'level': 'Critical',
                        'model': 'DatabaseError',

                    }
                )
                return redirect(self.request.get_full_path())


    

class ProcessedTransactions(TemplateView):
    template_name = 'Finance/processed_payments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            transactions = ProcessedPayments.objects.all().order_by('-processed_at')
            context['transactions'] = transactions
        except Exception as e:
            # Handle DatabaseError if needed
            messages.error(self.request, 'An error occurred. We are fixing it!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )

        return context

    def post(self, request, **kwargs):
        if self.request.method == 'POST':
            start_date_str = self.request.POST.get('from')  # Assuming 'from' is the field for start date
            end_date_str = self.request.POST.get('to')
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

            # Add one day to the end date to include transactions on that day
            end_date += timedelta(days=1)
            try:
                # Filter transactions within the date range
                transactions = ProcessedPayments.objects.filter(processed_at__range=[start_date, end_date]).order_by('-processed_at')

                context = {
                    'transactions': transactions
                }
                return render(self.request, self.template_name, context)
            except Exception as e:
                # Handle DatabaseError if needed
                messages.error(self.request, 'An error occurred. We are fixing it!')
                error_message = str(e)  # Get the error message as a string
                error_type = type(e).__name__

                logger.critical(
                    error_message,
                    exc_info=True,  # Include exception info in the log message
                    extra={
                        'app_name': __name__,
                        'url': self.request.get_full_path(),
                        'school': settings.SCHOOL_ID,
                        'error_type': error_type,
                        'user': self.request.user,
                        'level': 'Critical',
                        'model': 'DatabaseError',

                    }
                )
                return redirect(self.request.get_full_path())

    
class SuccesfulPayouts(TemplateView):
    template_name = 'Finance/succesful_payouts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            transactions = MpesaPayouts.objects.all().order_by('-date')
            context['transactions'] = transactions
        except Exception as e:
            # Handle DatabaseError if needed
            messages.error(self.request, 'An error occurred. We are fixing it!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )


        return context
    
    def post(self, request, **kwargs):
        if self.request.method == 'POST':
            start_date_str = self.request.POST.get('from')  # Assuming 'from' is the field for start date
            end_date_str = self.request.POST.get('to')
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

            # Add one day to the end date to include transactions on that day
            end_date += timedelta(days=1)
            try:
                # Filter transactions within the date range
                transactions = MpesaPayouts.objects.filter(date__range=[start_date, end_date]).order_by('-date')

                context = {
                    'transactions': transactions
                }
                return render(self.request, self.template_name, context)
            except Exception as e:
            # Handle DatabaseError if needed
                messages.error(self.request, 'An error occurred. We are fixing it!')
                error_message = str(e)  # Get the error message as a string
                error_type = type(e).__name__

                logger.critical(
                    error_message,
                    exc_info=True,  # Include exception info in the log message
                    extra={
                        'app_name': __name__,
                        'url': self.request.get_full_path(),
                        'school': settings.SCHOOL_ID,
                        'error_type': error_type,
                        'user': self.request.user,
                        'level': 'Critical',
                        'model': 'DatabaseError',

                    }
                )
                return redirect(self.request.get_full_path())

        

def initiated_payment_receipt(request, receipt):
    try:
        transaction = InitiatedPayments.objects.get(checkout_id=receipt)
        context = {
            'receipt':transaction
        }
        return render(request, 'Finance/initiated_receipts.html', context)
    except (InitiatedPayments.DoesNotExist, InitiatedPayments.MultipleObjectsReturned):
        messages.error(request, 'We could not find a transaction by this ID !!')
    except Exception as e:
            # Handle DatabaseError if needed
            messages.error(request, 'An error occurred. We are fixing it!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )


    return render(request, 'Finance/initiated_receipts.html')

def processed_payment_receipt(request, receipt):
    try:
        transaction = ProcessedPayments.objects.get(transaction_id=receipt)
        context = {
            'receipt':transaction
        }
        return render(request, 'Finance/processed_receipts.html', context)
    except (ProcessedPayments.DoesNotExist, ProcessedPayments.MultipleObjectsReturned):
        messages.error(request, 'We could not find a transaction by this ID !!')
    except Exception as e:
        # Handle DatabaseError if needed
        messages.error(request, 'An error occurred. We are fixing it!')
        error_message = str(e)  # Get the error message as a string
        error_type = type(e).__name__

        logger.critical(
            error_message,
            exc_info=True,  # Include exception info in the log message
            extra={
                'app_name': __name__,
                'url': request.get_full_path(),
                'school': settings.SCHOOL_ID,
                'error_type': error_type,
                'user': request.user,
                'level': 'Critical',
                'model': 'DatabaseError',

            }
        )
    return render(request, 'Finance/processed_receipts.html')
def payout_receipt(request, receipt):
    try:
        transaction = MpesaPayouts.objects.get(receipt=receipt)
        context = {
            'receipt':transaction
        }
        return render(request, 'Finance/payout_receipts.html', context)
    except (MpesaPayouts.DoesNotExist, MpesaPayouts.MultipleObjectsReturned):
        messages.error(request, 'We could not find a transaction by this ID !!')
    except Exception as e:
        # Handle DatabaseError if needed
        messages.error(request, 'An error occurred. We are fixing it!')
        error_message = str(e)  # Get the error message as a string
        error_type = type(e).__name__

        logger.critical(
            error_message,
            exc_info=True,  # Include exception info in the log message
            extra={
                'app_name': __name__,
                'url': request.get_full_path(),
                'school': settings.SCHOOL_ID,
                'error_type': error_type,
                'user': request.user,
                'level': 'Critical',
                'model': 'DatabaseError',

            }
        )
        return render(request, 'Finance/payout_receipts.html')
    


class CreateTerm(TemplateView):
    template_name = 'Finance/create_term.html'

    def post(self, request, **kwargs):
        if request.method == 'POST':
            year = request.POST.get('year')
            term = request.POST.get('term')
            starts_at = request.POST.get('from')
            ends_at = request.POST.get('to')

            try:
                term = Terms.objects.get(year=year, term=term)
                messages.error(request, f'{term} of Year {year} already exists. Click Manage Terms above to delete or edit term info.')
            except Terms.DoesNotExist:
                try:
                    term = Terms.objects.create(year=year, term=term, starts_at=starts_at, ends_at=ends_at)
                    messages.success(request, f'Succesfully created {term} for the year {year}')
                except Exception:
                    messages.error(request, f'We could not create this term, Please contact @support')
            except Exception as e:
            # Handle DatabaseError if needed
                messages.error(self.request, 'An error occurred. We are fixing it!')
                error_message = str(e)  # Get the error message as a string
                error_type = type(e).__name__

                logger.critical(
                    error_message,
                    exc_info=True,  # Include exception info in the log message
                    extra={
                        'app_name': __name__,
                        'url': self.request.get_full_path(),
                        'school': settings.SCHOOL_ID,
                        'error_type': error_type,
                        'user': self.request.user,
                        'level': 'Critical',
                        'model': 'DatabaseError',

                    }
                )

        return redirect('term-info', term.id)
    

class FeesListView(TemplateView):
    template_name = 'Finance/fees_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            fees = TermFeeStructure.objects.all().order_by('id')
            context['terms'] = fees
        except Exception as e:
            # Handle DatabaseError if needed
            messages.error(self.request, 'An error occurred. We are fixing it!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )

        return context
    
    def post(self, request, **kwargs):
        if request.method == 'POST':
            term = request.POST.get('term')
            year = request.POST.get('year')
            grade = request.POST.get('grade')
            try:
            
                fees = TermFeeStructure.objects.filter(term__term=term, term__year=year, grade=grade).order_by('-id')
                context = {
                    'terms':fees,
                    'term':term,
                    'grade':grade,
                    'year':year
                }
                if not fees:
                    messages.info(self.request, 'We could not find results matching your query !')

                return render(request, self.template_name, context)
            except Exception as e:
                # Handle DatabaseError if needed
                messages.error(self.request, 'An error occurred. We are fixing it!')
                error_message = str(e)  # Get the error message as a string
                error_type = type(e).__name__

                logger.critical(
                    error_message,
                    exc_info=True,  # Include exception info in the log message
                    extra={
                        'app_name': __name__,
                        'url': self.request.get_full_path(),
                        'school': settings.SCHOOL_ID,
                        'error_type': error_type,
                        'user': self.request.user,
                        'level': 'Critical',
                        'model': 'DatabaseError',

                    }
                )
                return redirect(self.request.get_full_path())
            



class SetFees(TemplateView):
    template_name = 'Finance/set_fees.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            structure = Terms.objects.all().order_by('-id')
            context['terms'] = structure
        except Exception as e:
            # Handle DatabaseError if needed
            messages.error(self.request, 'An error occurred. We are fixing it!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )
        return context
    
    def post(self, request, **kwargs):
        if request.method == 'POST':
            term_id = request.POST.get('term')
            grade = request.POST.get('grade')
            amount = request.POST.get('amount')
            term = Terms.objects.get(id=term_id)

            try:
                structure = TermFeeStructure.objects.get(term=term_id, grade=grade)
                messages.error(request, f'School fees for {term.term} - {term.year} has already been set. Click Manage Fees to edit or delete Fee Structure')
            except TermFeeStructure.DoesNotExist:
                structure = TermFeeStructure.objects.create(term=term, grade=grade, amount=amount)
            except Exception as e:
                # Handle DatabaseError if needed
                messages.error(self.request, 'An error occurred. We are fixing it!')
                error_message = str(e)  # Get the error message as a string
                error_type = type(e).__name__

                logger.critical(
                    error_message,
                    exc_info=True,  # Include exception info in the log message
                    extra={
                        'app_name': __name__,
                        'url': self.request.get_full_path(),
                        'school': settings.SCHOOL_ID,
                        'error_type': error_type,
                        'user': self.request.user,
                        'level': 'Critical',
                        'model': 'DatabaseError',

                    }
                )

            return redirect(request.get_full_path())

class ManageFees(TemplateView):
    template_name = 'Finance/manage_fees.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        structure_id = self.kwargs['id']
        try:
            structure = TermFeeStructure.objects.get(id=structure_id)
            context['fee'] = structure
        except Exception as e:
            # Handle DatabaseError if needed
            messages.error(self.request, 'An error occurred. We are fixing it!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )

        return context
    
    def post(self, request, **kwargs):
        if request.method == 'POST':
            structure_id = self.kwargs['id']
            payable = request.POST.get('amount')
            try:
                structure = TermFeeStructure.objects.get(id=structure_id)
                if 'edit' in request.POST:
                    
                    structure.amount = payable
                    structure.save()
                    return redirect(request.get_full_path())
                
                else:
                    structure.delete()
                    return redirect('fees-list')
            except (TermFeeStructure.DoesNotExist, TermFeeStructure.MultipleObjectsReturned):
                messages.error(self.request, 'Term Fee Structure Error !')
            except Exception as e:
                # Handle DatabaseError if needed
                messages.error(self.request, 'An error occurred. We are fixing it!')
                error_message = str(e)  # Get the error message as a string
                error_type = type(e).__name__

                logger.critical(
                    error_message,
                    exc_info=True,  # Include exception info in the log message
                    extra={
                        'app_name': __name__,
                        'url': self.request.get_full_path(),
                        'school': settings.SCHOOL_ID,
                        'error_type': error_type,
                        'user': self.request.user,
                        'level': 'Critical',
                        'model': 'DatabaseError',

                    }
                )
            
        return redirect(request.get_full_path())



class FeesHome(TemplateView):
    template_name = 'Finance/fees_home.html'
class SchoolFeeTransactions(TemplateView):
    template_name = 'Finance/fee_transactions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            transactions = StudentFeeMpesaTransaction.objects.all().order_by('-date')
            context['transactions'] = transactions
        except Exception as e:
            # Handle DatabaseError if needed
            messages.error(self.request, 'An error occurred. We are fixing it!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )

        return context
    
    
    def post(self, request, *args, **kwargs):
        # Get parameters from the form
        date_param = self.request.POST.get('date')
        receipt_param = self.request.POST.get('receipt')
        admission_number_param = self.request.POST.get('adm_no')
        phone = self.request.POST.get('phone')

        # Start with an empty filter dictionary
        filter_conditions = {}

        # Add conditions for provided parameters
        if date_param:
            filter_conditions['date__date'] = date_param

        if receipt_param:
            filter_conditions['receipt'] = receipt_param
        if phone:
            filter_conditions['phone'] = phone

        if admission_number_param:
            filter_conditions['adm_no'] = admission_number_param
        try:

            # Filter transactions based on the conditions
            transactions = StudentFeeMpesaTransaction.objects.filter(**filter_conditions).order_by('-date')

            # Add additional context if needed
            context = {
                'transactions': transactions,
            }
            return render(self.request, self.template_name, context)
        except Exception as e:
            # Handle DatabaseError if needed
            messages.error(self.request, 'An error occurred. We are fixing it!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )
            return redirect(self.request.get_full_path())
    
class ProcessedFeePayments(TemplateView):

    template_name = 'Finance/fee_payments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            transactions = StudentFeePayment.objects.all().order_by('-date')
            context['transactions'] = transactions
        except Exception as e:
            # Handle DatabaseError if needed
            messages.error(self.request, 'An error occurred. We are fixing it!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )

        return context
    def post(self, request, *args, **kwargs):
        # Get parameters from the form
        date_param = self.request.POST.get('date')
        receipt_param = self.request.POST.get('receipt')
        admission_number_param = self.request.POST.get('adm_no')
        phone = self.request.POST.get('phone')

        # Start with an empty filter dictionary
        filter_conditions = {}

        # Add conditions for provided parameters
        if date_param:
            filter_conditions['date__date'] = date_param

        if receipt_param:
            filter_conditions['transaction_id__receipt'] = receipt_param
        if phone:
            filter_conditions['transaction_id__phone'] = phone

        if admission_number_param:
            filter_conditions['transaction_id__adm_no'] = admission_number_param

        # Filter transactions based on the conditions
        try:
            transactions = StudentFeePayment.objects.filter(**filter_conditions).order_by('-date')

            # Add additional context if needed
            context = {
                'transactions': transactions,
            }

            return render(self.request, self.template_name, context)
        except Exception as e:
            # Handle DatabaseError if needed
            messages.error(self.request, 'An error occurred. We are fixing it!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )
            return redirect(self.request.get_full_path())
    
class ManageProcessedFeePayment(TemplateView):

    template_name = 'Finance/manage_fee_payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction_id = self.kwargs['id']
        try:
            transaction = StudentFeePayment.objects.get(id=transaction_id)
            number = ''.join(random.choices('0123456789', k=6))
            context['number'] = number
            context['transaction'] = transaction
        except Exception as e:
            # Handle DatabaseError if needed
            messages.error(self.request, 'An error occurred. We are fixing it!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )



        return context
    
    def post(self, request, **kwargs):
        if request.method == 'POST':
            
            adm_no = request.POST.get('adm_no')
            try:
                student = MyUser.objects.get(email=adm_no, role='Student')
                if 'verify' in request.POST:
                    
      

                        context = {
                            'student': student,
                            'transaction': self.get_context_data().get('transaction'),
                            'number':self.get_context_data().get('number'),
                            'adm_no':adm_no
                        }

                        return render(request, self.template_name, context=context)
            
                else:
                    transaction_id = self.kwargs['id']
                    otp = request.POST.get('random')
                    
                    if 'TRANSFER' == otp.upper():
                        transaction = StudentFeePayment.objects.get(id=transaction_id)
                        transaction.user = student
                        transaction.save()
                        messages.success(request, 'SUCCESS !')
                    else:
                        messages.error(request, 'You entered the wrong code. Try Again !')
            except MyUser.DoesNotExist:
                messages.error(request, 'Student with this Admission Number Does Not Exist !!')
            except Exception as e:
                # Handle DatabaseError if needed
                messages.error(self.request, 'An error occurred. We are fixing it!')
                error_message = str(e)  # Get the error message as a string
                error_type = type(e).__name__

                logger.critical(
                    error_message,
                    exc_info=True,  # Include exception info in the log message
                    extra={
                        'app_name': __name__,
                        'url': self.request.get_full_path(),
                        'school': settings.SCHOOL_ID,
                        'error_type': error_type,
                        'user': self.request.user,
                        'level': 'Critical',
                        'model': 'DatabaseError',

                    }
                )
            return redirect(request.get_full_path())

    
class ManageFeeTransaction(TemplateView):

    template_name = 'Finance/manage_fee_transaction.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction_id = self.kwargs['id']
        try:
            transaction = StudentFeeMpesaTransaction.objects.get(id=transaction_id)
            context['transaction'] = transaction
        except StudentFeeMpesaTransaction.DoesNotExist:
            messages.error(self.request, 'We could not find a transaction with this ID !!')
        except Exception as e:
            # Handle DatabaseError if needed
            messages.error(self.request, 'An error occurred. We are fixing it!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )


        return context
    

class StudentsFeeProfile(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'Finance/student_fee_profile.html'

    def test_func(self):
        return self.request.user.role != 'Teacher'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        email = self.kwargs['email']
        try:
            profile = StudentsFeeAccount.objects.get(user__email=email)
            context['profile'] = profile
        except StudentsFeeAccount.DoesNotExist:
            try:
                user = MyUser.objects.get(email=email, role='Student')
                profile = StudentsFeeAccount.objects.create(user=user)
                context['profile'] = profile
            except MyUser.DoesNotExist:
                messages.error(self.request, 'We could not find a user matching your query')
        except Exception as e:
            # Handle DatabaseError if needed
            messages.error(self.request, 'An error occurred. We are fixing it!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )
        transactions = StudentFeePayment.objects.filter(user__email=email)
        if not transactions:
            messages.info(self.request, 'This student has no transactions available')
        context['transactions'] = transactions
        

        return context


class SchoolFeesBalance(TemplateView):
    template_name = 'Finance/all_credit_fees.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        try:
            profiles = StudentsFeeAccount.objects.filter(balance__lt=0)
            balances = profiles.aggregate(balances=Sum('balance'))['balances']
            
            context['balance'] = balances
            context['profiles'] = profiles
            
        except Exception:
            messages.error(self.request, 'Database Error !! Contact @support')

        return context
    
    def post(self, request, **kwargs):
        if request.method == 'POST':
            limit = request.POST.get('limit')
            grade = request.POST.get('grade')
            if not limit and not grade:
                return redirect(self.request.get_full_path())
            
            else:
                try:
                    if not limit:
                        limit = 0
                    if int(limit) < 0:
                        profiles = StudentsFeeAccount.objects.filter(balance__lte=limit,balance__lt=0).order_by('balance')
                    else:

                        profiles = StudentsFeeAccount.objects.filter(balance__gte=limit).order_by('-balance')
                    balances = profiles.aggregate(balances=Sum('balance'))['balances']
                    if grade:
                        profiles = profiles.filter(user__academicprofile__current_class__grade=grade)
                        balance = profiles.aggregate(balances=Sum('balance'))['balances']
                        context ={
                            'profiles':profiles,
                            'limit':limit,
                            'grade':grade,
                            'balance':self.get_context_data().get('balance'),
                            'query_balance':balance
                        }
                    else:
                        balance = profiles.aggregate(balances=Sum('balance'))['balances']
                        context ={
                            'profiles':profiles,
                            'limit':limit,
                            'balance':self.get_context_data().get('balance'),
                            'query_balance':balance
                        }

                    return render(self.request, self.template_name, context )
                except Exception as e:
                    # Handle DatabaseError if needed
                    messages.error(self.request, str(e))
                    error_message = str(e)  # Get the error message as a string
                    error_type = type(e).__name__

                    logger.critical(
                        error_message,
                        exc_info=True,  # Include exception info in the log message
                        extra={
                            'app_name': __name__,
                            'url': self.request.get_full_path(),
                            'school': settings.SCHOOL_ID,
                            'error_type': error_type,
                            'user': self.request.user,
                            'level': 'Critical',
                            'model': 'DatabaseError',

                        }
                    )
                    return redirect(self.request.get_full_path())


class ClassFeeBalances(UserPassesTestMixin, TemplateView):
    template_name = 'Finance/class_fee_balances.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        class_id = self.kwargs['class_id']
        try:
            profiles = StudentsFeeAccount.objects.filter(user__academicprofile__current_class__class_name=class_id,
                                                        balance__lt=0)
            balances = profiles.aggregate(balances=Sum('balance'))['balances']
            
            context['balance'] = balances
            if not profiles:
                    messages.error(self.request, 'We could not find results matching your query.')
            context['profiles'] = profiles
            context['class_id'] = class_id
        except Exception as e:
            # Handle DatabaseError if needed
            messages.error(self.request, 'An error occurred. We are fixing it!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )


        return context
    def post(self, request, **kwargs):
        if request.method == 'POST':
            class_id = self.kwargs['class_id']
            limit = request.POST.get('limit')  
            try:
                profiles = StudentsFeeAccount.objects.filter(user__academicprofile__current_class__class_name=class_id,balance__lt=limit)
                balances = profiles.aggregate(balances=Sum('balance'))['balances']
            
                context = {
                    'profiles':profiles,
                    'limit':limit,
                    'class_id':class_id,
                    'balance':self.get_context_data().get('balance'),
                    'query_balance':balances
                }
                if not profiles:
                    messages.error(self.request, 'We could not find results matching your query.')
                
                return render(self.request, self.template_name, context)
            except Exception as e:
                # Handle DatabaseError if needed
                messages.error(self.request, 'An error occurred. We are fixing it!')
                error_message = str(e)  # Get the error message as a string
                error_type = type(e).__name__

                logger.critical(
                    error_message,
                    exc_info=True,  # Include exception info in the log message
                    extra={
                        'app_name': __name__,
                        'url': self.request.get_full_path(),
                        'school': settings.SCHOOL_ID,
                        'error_type': error_type,
                        'user': self.request.user,
                        'level': 'Critical',
                        'model': 'DatabaseError',

                    }
                )
                return redirect(self.request.get_full_path())


    def test_func(self):
        user = self.request.user
        class_name = self.kwargs['class_id']
        try:
            class_id = SchoolClass.objects.filter(class_teacher=user, class_name=class_name)
            return class_id
        except Exception as e:
            # Handle DatabaseError if needed
            messages.error(self.request, 'An error occurred. We are fixing it!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )
            return False
        

class AddFeePayment(TemplateView):
    template_name = 'Finance/add_fee_payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.kwargs['email']
        context['student'] = MyUser.objects.get(email=email)


        return context
    
    def post(self, *args, **kwargs):
        if self.request.method == 'POST':
            try:
                if 'mpesa' in self.request.POST:
                    transaction_id = self.request.POST.get('transaction_id')
                    student = self.get_context_data().get('student')
                    phone = self.request.POST.get('phone')
                    adm_no = self.request.POST.get('adm_no')
                    paid_on = self.request.POST.get('date')
                    amount = self.request.POST.get('amount')

                    payment = StudentFeeMpesaTransaction.objects.create(receipt=transaction_id, amount=amount,
                                                                        phone=phone, adm_no=adm_no,date=paid_on)
                    
                elif 'bank' in self.request.POST:
                    pass
                    
            except Exception as e:
                messages.error(self.request, str(e))
                return redirect(self.request.get_full_path())



        return redirect('students-view')



