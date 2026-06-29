# apps/accounts/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class LogoutProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Prevent caching for authenticated pages
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response

class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to view any page other
    than the exempted URLs (like the landing page, login, register, etc.).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Whitelisted exact paths or prefixes
        exempt_urls = [
            '/',  # Landing page
            '/accounts/login/',
            '/accounts/register/',
            '/accounts/password-reset/',
        ]
        
        path = request.path_info

        if not request.user.is_authenticated:
            # Check if path starts with any of the exempt prefixes (for things like /password-reset/done/)
            is_exempt = False
            for url in exempt_urls:
                if path == url or (url != '/' and path.startswith(url)):
                    is_exempt = True
                    break
                    
            if not is_exempt and not path.startswith('/admin/') and not path.startswith('/static/') and not path.startswith('/media/'):
                return redirect(f'/accounts/login/?next={path}')

        return self.get_response(request)