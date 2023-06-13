from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt




urlpatterns = [
    path('', views.index, name="expenses"),
    path('add_expense', views.add_expense, name="add_expense"),
    path('edit-expense/<int:id>', views.expense_edit, name="expense-edit"),
    path('expense-delete/<int:id>', views.delete_expense, name="expense-delete"),
    path('search-expenses', csrf_exempt(views.search_expenses), name="search_expenses")
]