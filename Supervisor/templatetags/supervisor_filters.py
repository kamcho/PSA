from django import template
from Finance.models import Invoices

from Users.models import MyUser, StudentsFeeAccount


register = template.Library()
# logger = logging.getLogger('django')

@register.filter
def get_fee_balances(user):
    balances = StudentsFeeAccount.objects.filter(balance_gte=1)
    all_users = MyUser.objects.filter(role='Student')
    percentage = (balances.count() / all_users.count() )* 100

    return round(percentage)


@register.filter
def get_invoice_balances(user):
    invoices = Invoices.objects.all()
    balances = invoices.filter(balance_gt=0)
    percentage = (balances.count() / invoices.count()) * 100

    return round(percentage)
