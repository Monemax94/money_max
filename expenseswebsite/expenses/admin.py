from django.contrib import admin
from .models import Expense, Category
# Register your models here.


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('category', 'description', 'amount', 'date', 'owner' )
    search_fields = ('category', 'description', 'amount', 'date', 'owner' )

    list_per_page = 5
    
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Category)