from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
from userpreferences.models import UserPreference
from datetime import *
from django.utils import timezone

# Usage example
# date_str = '2023-06-18'
# date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

# CSV file conversion utility import
import csv
# Excel file conversion utility import
import xlwt
# PDF file conversion utility import
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum

def search_expenses(request):
    """
    Search expenses based on the provided search string.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - JsonResponse: JSON response containing the matching expenses.
    """
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    """
    View function for displaying the expenses.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - HttpResponse: Rendered response with the expenses and pagination.
    """
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    try:
        user_preference = UserPreference.objects.get(user=request.user)
        currency = user_preference.currency
    except UserPreference.DoesNotExist:
        currency = None

    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency,
    }
    return render(request, 'expenses/index.html', context)


@login_required(login_url='/authentication/login')
def add_expense(request):
    """
    View function for adding a new expense.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - HttpResponse: Rendered response for adding an expense.
    - HttpResponseRedirect: Redirects to the expense list after adding an expense.
    """
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }

    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date_str = request.POST['expense_date']
        category = request.POST['category']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', context)

        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'expenses/add_expense.html', context)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format! The date must be in YYYY-MM-DD format.')
            return render(request, 'expenses/add_expense.html', context)

        Expense.objects.create(owner=request.user, amount=amount, date=date, category=category, description=description)
        messages.success(request, 'Expense added successfully')
        return redirect('expenses')


@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    """
    View function for editing an expense.

    Parameters:
    - request: The HTTP request object.
    - id: The ID of the expense to be edited.

    Returns:
    - HttpResponse: Rendered response for editing an expense.
    - HttpResponseRedirect: Redirects to the expense list after editing an expense.
    """
    try:
        expense = Expense.objects.get(pk=id, owner=request.user)
    except Expense.DoesNotExist:
        messages.error(request, 'Expense does not exist!')
        return redirect('expenses')

    categories = Category.objects.all()
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date_str = request.POST.get('expense_date')
        category = request.POST.get('category')

        if not amount:
            messages.error(request, 'Amount is required!')
        elif not description:
            messages.error(request, 'Description is required!')
        elif not date_str:
            messages.error(request, 'Date is required!')
        else:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                expense.amount = amount
                expense.description = description
                expense.date = date
                expense.category = category
                expense.save()
                messages.success(request, 'Expense updated successfully!')
                return redirect('expenses')
            except ValueError:
                messages.error(request, 'Invalid date format! The date must be in YYYY-MM-DD format.')

    context = {
        'expense': expense,
        'categories': categories,
        'values': expense,
    }
    return render(request, 'expenses/edit-expense.html', context)


def delete_expense(request, id):
    """
    View function for deleting an expense.

    Parameters:
    - request: The HTTP request object.
    - id: The ID of the expense to be deleted.

    Returns:
    - HttpResponseRedirect: Redirects to the expense list after deleting an expense.
    """
    try:
        expense = Expense.objects.get(pk=id, owner=request.user)
        expense.delete()
        messages.success(request, 'Expense deleted!')
    except Expense.DoesNotExist:
        messages.error(request, 'Expense does not exist!')
    return redirect('expenses')


def expense_category_summary(request):
    """
    View function for generating the expense category summary.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - JsonResponse: JSON response containing the expense category data.
    """
    today = date.today()
    six_months_ago = today - timedelta(days=30 * 6)

    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=six_months_ago,
                                      date__lte=today)

    finalrep = {}
    for expense in expenses:
        category = expense.category
        if category in finalrep:
            finalrep[category] += expense.amount
        else:
            finalrep[category] = expense.amount

    return JsonResponse({'expense_category_data': finalrep}, safe=False)


def stats_view(request):
    """
    View function for displaying expense statistics.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - HttpResponse: Rendered response for displaying expense statistics.
    """
    return render(request, 'expenses/stats.html')


def export_csv(request):
    """
    View function for exporting expenses as a CSV file.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - HttpResponse: CSV file response containing the expenses.
    """
    now = timezone.now().strftime('%Y-%m-%d_%H-%M-%S')  # Format the current datetime
    filename = 'Expenses_{}.csv'.format(now)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'inline; attachment; filename="{}"'.format(filename)

    writer = csv.writer(response)
    writer.writerow(['AMOUNT', 'DESCRIPTION', 'CATEGORY', 'DATE'])

    expenses = Expense.objects.filter(owner=request.user)

    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.date])

    return response


def export_excel(request):
    """
    View function for exporting expenses as an Excel file.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - HttpResponse: Excel file response containing the expenses.
    """
    import datetime

    response = HttpResponse(content_type='application/ms-excel')
    current_datetime = datetime.datetime.now()
    file_name = 'Expenses_' + current_datetime.strftime('%Y-%m-%d_%H-%M-%S') + '.xls'
    response['Content-Disposition'] = 'inline; attachment; filename=' + file_name

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['AMOUNT', 'DESCRIPTION', 'CATEGORY', 'DATE']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Expense.objects.filter(owner=request.user).values_list(
        'amount', 'description', 'category', 'date')

    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)

    return response


def export_pdf(request):
    """
    View function for exporting expenses as a PDF file.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - HttpResponse: PDF file response containing the expenses.
    """
    import datetime

    response = HttpResponse(content_type='application/pdf')
    current_datetime = datetime.datetime.now()
    file_name = 'Expenses_' + current_datetime.strftime('%Y-%m-%d_%H-%M-%S') + '.pdf'
    response['Content-Disposition'] = 'inline; filename=' + file_name

    response['Content-Transfer-Encoding'] = 'binary'

    expenses = Expense.objects.filter(owner=request.user)

    total = expenses.aggregate(Sum('amount'))

    html_string = render_to_string(
        'expenses/pdf-output.html', {'expenses': expenses, 'total': total['amount__sum']})
    html = HTML(string=html_string)

    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')
        response.write(output.read())

    return response
