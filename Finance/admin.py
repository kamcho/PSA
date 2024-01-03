from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(MpesaPayouts)
admin.site.register(InitiatedPayments)
admin.site.register(ProcessedPayments)
admin.site.register(StudentFeeMpesaTransaction)
admin.site.register(StudentFeePayment)
admin.site.register(TermFeeStructure)
admin.site.register(Invoices)
admin.site.register(InvoicePayments)