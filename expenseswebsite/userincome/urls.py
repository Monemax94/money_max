from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt




urlpatterns = [
    path('', views.index, name="income"),
    path('add_income', views.add_income, name="add_income"),
    path('income-edit/<int:id>', views.income_edit, name="income-edit"),
    path('income-delete/<int:id>', views.delete_income, name="income-delete"),
    path('search-income', csrf_exempt(views.search_income), name="search_income"),
    path('income_source_summary', views.income_source_summary, name="income_source_summary"),
    path('income_stats', views.income_stats_view, name="income_stats"),
    path('income_export_csv', views.income_export_csv, name="income_export_csv"),
    path('income_export_excel', views.income_export_excel, name="income_export_excel"),
    path('income_export_pdf', views.income_export_pdf, name="income_export_pdf"),
    
]