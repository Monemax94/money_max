# Importing necessary modules
from django.shortcuts import render
import os
import json
from django.conf import settings
from .models import UserPreference
from django.contrib import messages

def index(request):
    """
    View function for the preferences index page.

    Renders the preferences index page with currency data and user preferences.

    :param request: The HTTP request object.
    :return: Rendered HTML response.
    """

    # Load currency data from JSON file
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')

    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        for k, v in data.items():
            currency_data.append({'name': k, 'value': v})

    # Check if user preferences exist
    exists = UserPreference.objects.filter(user=request.user).exists()
    user_preferences = None
    if exists:
        user_preferences = UserPreference.objects.get(user=request.user)

    if request.method == 'GET':
        # Render the preferences index page with currency data and user preferences
        return render(request, 'preferences/index.html', {'currencies': currency_data, 'user_preferences': user_preferences})
    else:
        # Process form submission to update user preferences
        currency = request.POST['currency']

        if exists:
            # Update existing user preferences
            user_preferences.currency = currency
            user_preferences.save()
        else:
            # Create new user preferences
            UserPreference.objects.create(user=request.user, currency=currency)
        
        messages.success(request, 'Changes saved')
        # Render the preferences index page with updated currency data and user preferences
        return render(request, 'preferences/index.html', {'currencies': currency_data, 'user_preferences': user_preferences})
