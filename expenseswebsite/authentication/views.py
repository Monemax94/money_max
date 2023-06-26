from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.contrib import auth
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator
from django.contrib.auth.tokens import PasswordResetTokenGenerator

# Create your views here.

class EmailValidationView(View):
    """
    View to validate email address.
    """
    def post(self, request):
        """
        POST request to validate email.
        """
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Sorry, email already in use. Please choose another one'}, status=409)

        return JsonResponse({'email_valid': True })


class UsernameValidationView(View):
    """
    View to validate username.
    """
    def post(self, request):
        """
        POST request to validate username.
        """
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Username should only contain alphanumeric characters'}, status=400)
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'Sorry, username already in use. Please choose another one'}, status=409)

        return JsonResponse({'username_valid': True })


class RegisterationView(View):
    """
    View for user registration.
    """
    def get(self, request):
        """
        GET request to render registration page.
        """
        return render(request, 'authentication/register.html')
    
    def post(self, request):
        """
        POST request to create a user account.
        """
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():

                if len(password) < 6:
                    messages.error(request, 'Password is too short!')
                    return render(request, 'authentication/register.html', context)
                
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()

                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                domain = get_current_site(request).domain
                link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token_generator.make_token(user)})
                activate_url = 'http://' + domain + link

                email_body = 'Hi ' + user.username + ', Please use this link to activate your account:\n' + activate_url
                email_subject = 'Activate your account'
                
                email = EmailMessage(
                    email_subject, email_body, "noreply@moneymax.com",
                    [email],
                )
                email.send(fail_silently=False)

                messages.success(request, 'Account successfully created! Check your email to activate your account and login!')
                return render(request, 'authentication/register.html')

        return render(request, 'authentication/register.html')


class VerificationView(View):
    """
    User email verification view.
    """
    def get(self, request, uidb64, token):
        """
        GET request to verify user email.
        """
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                return redirect('login' + '?message' + 'User already activated')

            if user.is_active:
                return redirect('login')
            
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect('login')

        except Exception as ex:
            pass

        return redirect('login')
    

class LoginView(View):
    """
    User login view.
    """
    def get(self, request):
        """
        GET request to render login page.
        """
        return render(request, 'authentication/login.html')
    
    def post(self, request):
        """
        POST request to authenticate user login.
        """
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome, ' + user.username + ' you are now logged in.')
                    return redirect('expenses')
            
                messages.error(request, 'Account is not active, please check your email')
                return render(request, 'authentication/login.html')
            
            messages.error(request, 'Invalid credentials, please try again.')
            return render(request, 'authentication/login.html')
         
        messages.error(request, 'Please fill in all fields and try again.')
        return render(request, 'authentication/login.html')


class LogoutView(View):
    """
    User logout view.
    """
    def post(self, request):
        """
        POST request to log out the user.
        """
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')
    


class RequestPasswordResetEmail(View):
    """
    View for requesting a password reset email.
    """
    def get(self, request):
        """
        GET request to render password reset page.
        """
        return render(request, 'authentication/reset-password.html')
    
    def post(self, request):
        """
        POST request to send a password reset email.
        """
        email = request.POST['email']

        context = {
            'values': request.POST
        }

        if not validate_email(email):
            messages.error(request, 'Please provide a valid email')
            return render(request, 'authentication/reset-password.html', context)
        
        current_site = get_current_site(request)
        user = User.objects.filter(email=email)
        
        if user.exists():
            email_contents = {
                'user': user[0],
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0]),
            }

        link = reverse('reset-user-password', kwargs={
            'uidb64': email_contents['uid'], 'token': email_contents['token']})

        email_subject = 'Password reset information'
        reset_url = 'http://' + current_site.domain + link

        email = EmailMessage(
            email_subject,
            'Hi there, Please click the link below to reset your password:\n' + reset_url,
            'noreply@semycolon.com',
            [email],
        )
        email.send(fail_silently=False)

        messages.success(request, 'We have sent you a password reset email')

        return render(request, 'authentication/reset-password.html')


class CompletePasswordReset(View):
    """
    View to complete the password reset process.
    """
    def get(self, request, uidb64, token):
        """
        GET request to render password reset form.
        """
        context = {
            'uidb64': uidb64,
            'token': token
        }

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, 'Password reset link is invalid, please request a new one.')
                return render(request, 'authentication/reset-password.html')

        except DjangoUnicodeDecodeError as identifier:
            messages.error(request, 'An error occurred, please try again.')
        
        return render(request, 'authentication/set-new-password.html', context)
    
    def post(self, request, uidb64, token):
        """
        POST request to set a new password.
        """
        context = {
            'uidb64': uidb64,
            'token': token
        }

        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'authentication/set-new-password.html', context)

        if len(password) < 6:
            messages.error(request, 'Password is too short')
            return render(request, 'authentication/set-new-password.html', context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful. You can now login with your new password')
            return redirect('login')
        
        except DjangoUnicodeDecodeError as identifier:
            messages.error(request, 'An error occurred, please try again.')
            return render(request, 'authentication/set-new-password.html', context)
