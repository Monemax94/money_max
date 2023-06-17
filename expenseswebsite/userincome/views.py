from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Source, Userincome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
import json
from django.http import JsonResponse
from datetime import datetime

# Create your views here. add_income



def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = Userincome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Userincome.objects.filter(
            date__istartswith=search_str, owner=request.user) | Userincome.objects.filter(
            description__icontains=search_str, owner=request.user) | Userincome.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
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



@login_required(login_url='/authentication/login')
def add_income(request):
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


@login_required(login_url='/authentication/login')
def income_edit(request, id):
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
                return redirect('expenses')
            except ValueError:
                messages.error(request, 'Invalid date format! The date must be in YYYY-MM-DD format.')

    context = {
        'income': income,
        'sources': sources,
        'values': income,
    }
    return render(request, 'income/edit_income.html', context)


def delete_income(request, id):
    income = Userincome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'income removed')
    return redirect('income')
