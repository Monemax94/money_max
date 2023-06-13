from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse



def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith = search_str, owner = request.user ) | Expense.objects.filter(
            date__istartswith = search_str, owner = request.user ) | Expense.objects.filter(
            description__icontains = search_str, owner = request.user ) | Expense.objects.filter(
            category__icontains = search_str, owner = request.user ) 
        data = expenses.values()
        return JsonResponse(list(data), safe=False)
 



@login_required(login_url='/authentication/login')
def index(request):
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    context = {
        'expenses': expenses,
        'page_obj': page_obj
    }
    return render(request, 'expenses/index.html', context)

def add_expense(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('expense_date')
        category = request.POST.get('category')

        if not amount:
            messages.error(request, 'Amount is required!')
        elif not description:
            messages.error(request, 'Description is required!')
        else:
            expense = Expense.objects.create(owner=request.user, amount=amount, date=date, category=category, description=description)
            messages.success(request, 'Expense saved successfully!')
            return redirect('expenses')
    
    context = {
        'categories': categories,
        'values': request.POST
    }
    return render(request, 'expenses/add_expense.html', context)

def expense_edit(request, id):
    try:
        expense = Expense.objects.get(pk=id, owner=request.user)
    except Expense.DoesNotExist:
        messages.error(request, 'Expense does not exist!')
        return redirect('expenses')

    categories = Category.objects.all()
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('expense_date')
        category = request.POST.get('category')

        if not amount:
            messages.error(request, 'Amount is required!')
        elif not description:
            messages.error(request, 'Description is required!')
        else:
            expense.amount = amount
            expense.description = description
            expense.date = date
            expense.category = category
            expense.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('expenses')

    context = {
        'expense': expense,
        'categories': categories,
        'values': expense,
    }
    return render(request, 'expenses/edit-expense.html', context)

def delete_expense(request, id):
    try:
        expense = Expense.objects.get(pk=id, owner=request.user)
        expense.delete()
        messages.success(request, 'Expense deleted!')
    except Expense.DoesNotExist:
        messages.error(request, 'Expense does not exist!')
    return redirect('expenses')
