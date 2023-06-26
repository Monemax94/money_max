from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Source, Userincome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
import json
from django.http import JsonResponse, HttpResponse
from datetime import *
from django.utils import timezone

# Usage example
# date_str = '2023-06-18'
# date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

# csv file conversion utility import
import csv
# Excelfile conversion utility import
import xlwt
# pdf file conversion utility import
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum

# Search income
def search_income(request):
    """
    View function for searching income.

    Searches income based on the provided search text in the request body.

    :param request: The HTTP request object.
    :return: JSON response with the search results.
    """
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = Userincome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Userincome.objects.filter(
            date__istartswith=search_str, owner=request.user) | Userincome.objects.filter(
            description__icontains=search_str, owner=request.user) | Userincome.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)

# Index page
@login_required(login_url='/authentication/login')
def index(request):
    """
    View function for the income index page.

    Renders the income index page with income data.

    :param request: The HTTP request object.
    :return: Rendered HTML template for the income index page.
    """
    sources = Source.objects.all()
    income = Userincome.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except UserPreference.DoesNotExist:
        currency = 'USD'
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'income/index.html', context)

# Add income
@login_required(login_url='/authentication/login')
def add_income(request):
    """
    View function for adding income.

    Handles both GET and POST requests. Renders the add income form and creates a new income object respectively.

    :param request: The HTTP request object.
    :return: Rendered HTML template or redirection to income index.
    """
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }

    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date_str = request.POST['income_date']
        source = request.POST['source']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)

        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'income/add_income.html', context)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format! The date must be in YYYY-MM-DD format.')
            return render(request, 'income/add_income.html', context)

        Userincome.objects.create(owner=request.user, amount=amount, date=date, source=source, description=description)
        messages.success(request, 'Income added successfully')
        return redirect('income')

# Edit income
@login_required(login_url='/authentication/login')
def income_edit(request, id):
    """
    View function for editing income.

    Handles both GET and POST requests. Renders the edit income form and updates the income object respectively.

    :param request: The HTTP request object.
    :param id: The ID of the income to be edited.
    :return: Rendered HTML template or redirection to income index.
    """
    try:
        income = Userincome.objects.get(pk=id, owner=request.user)
    except Userincome.DoesNotExist:
        messages.error(request, 'Income does not exist!')
        return redirect('income')

    sources = Source.objects.all()
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date_str = request.POST.get('income_date')
        source = request.POST.get('source')

        if not amount:
            messages.error(request, 'Amount is required!')
        elif not description:
            messages.error(request, 'Description is required!')
        elif not date_str:
            messages.error(request, 'Date is required!')
        else:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                income.amount = amount
                income.description = description
                income.date = date
                income.source = source
                income.save()
                messages.success(request, 'Income updated successfully!')
                return redirect('income')
            except ValueError:
                messages.error(request, 'Invalid date format! The date must be in YYYY-MM-DD format.')

    context = {
        'income': income,
        'sources': sources,
        'values': income,
    }
    return render(request, 'income/edit_income.html', context)

# Delete income
def delete_income(request, id):
    """
    View function for deleting income.

    Deletes the specified income object.

    :param request: The HTTP request object.
    :param id: The ID of the income to be deleted.
    :return: Redirection to income index.
    """
    income = Userincome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Income removed')
    return redirect('income')

# Income source summary
def income_source_summary(request):
    """
    View function for generating income source summary.

    Calculates the total income for each income source in the last six months.

    :param request: The HTTP request object.
    :return: JSON response with the income source data.
    """
    today = date.today()
    six_months_ago = today - timedelta(days=30*6)

    userincome = Userincome.objects.filter(owner=request.user,
                                      date__gte=six_months_ago,
                                      date__lte=today)

    finalrep = {}
    for income in userincome:
        source = income.source
        if source in finalrep:
            finalrep[source] += income.amount
        else:
            finalrep[source] = income.amount

    return JsonResponse({'income_source_data': finalrep}, safe=False)

# Income statistics view
def income_stats_view(request):
    """
    View function for the income statistics page.

    Renders the income statistics page.

    :param request: The HTTP request object.
    :return: Rendered HTML template for the income statistics page.
    """
    return render(request, 'income/income_stats.html')

# Export income to CSV
def income_export_csv(request):
    """
    View function for exporting income data to CSV.

    Generates a CSV file with the income data.

    :param request: The HTTP request object.
    :return: HTTP response with the CSV file.
    """
    now = timezone.now().strftime('%Y-%m-%d_%H-%M-%S')  # Format the current datetime
    filename = 'Expenses_{}.csv'.format(now)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'inline; attachment; filename="{}"'.format(filename)

    writer = csv.writer(response)
    writer.writerow(['AMOUNT', 'DESCRIPTION', 'CATEGORY', 'DATE'])

    incomes = Userincome.objects.filter(owner=request.user)

    for income in incomes:
        writer.writerow([income.amount, income.description, income.source, income.date])

    return response

# Export income to Excel
def income_export_excel(request):
    """
    View function for exporting income data to Excel.

    Generates an Excel file with the income data.

    :param request: The HTTP request object.
    :return: HTTP response with the Excel file.
    """
    import datetime

    response = HttpResponse(content_type='application/ms-excel')
    current_datetime = datetime.datetime.now()
    file_name = 'Incomes_' + current_datetime.strftime('%Y-%m-%d_%H-%M-%S') + '.xls'
    response['Content-Disposition'] = 'inline; attachment; filename=' + file_name

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Incomes')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['AMOUNT', 'DESCRIPTION', 'CATEGORY', 'DATE']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Userincome.objects.filter(owner=request.user).values_list(
        'amount', 'description', 'source', 'date')

    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)

    return response

# Export income to PDF
def income_export_pdf(request):
    """
    View function for exporting income data to PDF.

    Generates a PDF file with the income data.

    :param request: The HTTP request object.
    :return: HTTP response with the PDF file.
    """
    import datetime

    response = HttpResponse(content_type='application/pdf')
    current_datetime = datetime.datetime.now()
    file_name = 'Incomes_' + current_datetime.strftime('%Y-%m-%d_%H-%M-%S') + '.pdf'
    response['Content-Disposition'] = 'inline; filename=' + file_name

    response['Content-Transfer-Encoding'] = 'binary'

    incomes = Userincome.objects.filter(owner=request.user)

    total = incomes.aggregate(Sum('amount'))

    html_string = render_to_string(
        'income/pdf-output.html', {'incomes': incomes, 'total': total['amount__sum']})
    html = HTML(string=html_string)

    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')
        response.write(output.read())

    return response
