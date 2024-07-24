from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

class CustomAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)

        if header is None:
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE']) or None
        else:
            raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token), validated_token
    
    def get_validated_token(self, raw_token):
        validated_token = super().get_validated_token(raw_token)
        jti = validated_token['jti']

        # Check if the token is blacklisted
        if BlacklistedToken.objects.filter(token__jti=jti).exists():
            raise AuthenticationFailed('Token is blacklisted')

        return validated_token

    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if user is None or not user.is_active:
            raise AuthenticationFailed('User inactive or deleted.')
        return user