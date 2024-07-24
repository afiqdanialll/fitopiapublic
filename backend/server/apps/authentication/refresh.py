from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import JsonResponse
import requests

class RefreshTokenMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # Define the logout URL or path
        logout_url = '/api/authentication/logout/'

        # Check if the request path is for the logout endpoint
        if request.path == logout_url:
            return None
        # Get tokens from cookies
        access_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
        refresh_token = request.COOKIES.get('refresh_token')

        if not access_token:
            if refresh_token:
                try: 
                    # Make a request to the token refresh endpoint
                    response = requests.post(
                        request.build_absolute_uri('/api/authentication/token_refresh/'),
                        data={'refresh': refresh_token}
                    )
                    if response.status_code == 200:
                        # Get new access token from the response
                        new_access_token = response.json().get('access')
                        
                        # Update the request to use the new access token
                        request.META['HTTP_AUTHORIZATION'] = f'Bearer {new_access_token}'

                        # Set the new access token in the response cookies
                        response = JsonResponse({'access': new_access_token})
                        response.set_cookie(
                            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
                            value=new_access_token,
                            max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
                            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                        )
                        # Return the response so that it gets sent to the client
                        return response
                    else:
                        return JsonResponse({'error': 'Unable to refresh access token'}, status=response.status_code)
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=500)

        return None
