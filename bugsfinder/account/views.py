import json
import logging
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from smtplib import SMTPException

from django.contrib.auth import authenticate, login, logout
from django.db import DatabaseError, connection, transaction
from account.models import User
from account.models import Report
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from account.serializers import UserSerializer
from account.serializers import UserProfileSerializer
from account.serializers import UserReportSerializer
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.conf import settings
from account.utils import send_activation_email
from django.http import HttpResponseRedirect



# custom
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)


def activation_redirect(parameter, message):
    query = urlencode({parameter: message})
    return HttpResponseRedirect(
        f"{settings.FRONTEND_URL.rstrip('/')}/#/?{query}"
    )


@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({'success':'CSRF Cookie Set'})


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except DatabaseError:
            logger.exception("Bugs Finder health check could not reach its database.")
            return Response(
                {"status": "unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


# Generate Token Manually
def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
  }

# @method_decorator(csrf_protect, name='dispatch')
class CheckAuthenticatedView(APIView):
    permission_classes=[AllowAny]
    def get(self, request):
        if request.user.is_authenticated:
            return Response({'isAuthenticated': True})
        else:
            return Response({'isAuthenticated': False})
 
# @method_decorator(csrf_protect, name='dispatch')
class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            if (
                settings.EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend"
                and not (settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD)
            ):
                return Response(
                    {"detail": "Account activation email is not configured on the server."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            try:
                with transaction.atomic():
                    user = serializer.save()
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    activation_link = reverse(
                        'activate', kwargs={'uid': uid, 'token': token}
                    )
                    activation_url = f'{settings.SITE_DOMAIN}{activation_link}'
                    send_activation_email(user.email, activation_url, uid, token)
            except (SMTPException, OSError):
                logger.exception("Could not send a Bugs Finder activation email.")
                return Response(
                    {"detail": "Could not send the activation email. Check the server's SMTP configuration."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            
            return Response({'data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @method_decorator(csrf_protect, name='dispatch')
class ActivateView(APIView):
    permission_classes = [AllowAny]
    def get(self,request,uid,token):
        if not uid or not token:
            return Response({'detail': 'Missing uid or token.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                if user.is_active:
                    return activation_redirect(
                        "alreadymessage", "Account Is Already Activated"
                    )
                user.is_active = True
                user.save()
                return activation_redirect(
                    "message", "Account Successfully Activated"
                )
            else:
                return activation_redirect("errmessage", "Invalid Activation Link")
        except (User.DoesNotExist, ValueError):
            return activation_redirect("errmessage", "Invalid Activation Link")
        


# @method_decorator(csrf_protect, name='dispatch')
class ActivationConfirm(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        if not uid or not token:
            return Response({'detail': 'Missing uid or token.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                if user.is_active:
                    return Response({'detail': 'Account is already activated.'}, status=status.HTTP_200_OK)
 
                user.is_active = True
                user.save()
                
                return activation_redirect(
                    "message", "Account Successfully Activated"
                )
            else:
                return activation_redirect("errmessage", "Invalid Activation Link")
        except (User.DoesNotExist, ValueError):
            return activation_redirect("errmessage", "Invalid Activation Link")
        

# @method_decorator(csrf_protect, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

    


    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'detail': 'Email and Password is required.'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    token2 = get_tokens_for_user(user)
                    # session_key = request.session.session_key
                    # print(session_key)
                    # print(token2)
                    
                    return Response({'detail':'Logged in successfully.','token2':token2 },status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'Please Activate Your Account.'}, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({'detail': 'Email or Password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)


    
        
class UserDetailView(APIView):
  
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    def post(self,request):
        logout(request)
        return Response({'detail':'Logged Out Successfully'},status.HTTP_200_OK)


class ReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        report = Report.objects.filter(user=request.user)
        serializer = UserReportSerializer(report, many=True)
        return Response({'data':serializer.data}, status=status.HTTP_200_OK)
    

    def post(self, request):
        serializer = UserReportSerializer(data=request.data)
        if serializer.is_valid():
            report = serializer.save(user=request.user)
            return Response(
                {'data': UserReportSerializer(report).data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CodeAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = request.data.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            return Response(
                {"detail": "A non-empty prompt is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(prompt) > 50000:
            return Response(
                {"detail": "The prompt must be 50,000 characters or fewer."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not settings.GEMINI_API_KEY:
            return Response(
                {"detail": "Code analysis is not configured. Set GEMINI_API_KEY."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.5,
                "topP": 1,
                "topK": 40,
                "maxOutputTokens": 2000,
            },
        }
        provider_request = Request(
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.GEMINI_MODEL}:generateContent",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": settings.GEMINI_API_KEY,
            },
            method="POST",
        )

        try:
            with urlopen(provider_request, timeout=30) as provider_response:
                provider_payload = json.loads(
                    provider_response.read().decode("utf-8")
                )
        except HTTPError as error:
            logger.warning("Gemini returned HTTP %s during code analysis.", error.code)
            return Response(
                {"detail": "The code analysis provider rejected the request."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except URLError:
            logger.exception("Could not reach the Gemini code analysis provider.")
            return Response(
                {"detail": "Could not reach the code analysis provider."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except (UnicodeDecodeError, json.JSONDecodeError):
            logger.exception("Gemini returned an invalid response.")
            return Response(
                {"detail": "The code analysis provider returned an invalid response."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if not isinstance(provider_payload, dict):
            logger.warning("Gemini response was not a JSON object.")
            return Response(
                {"detail": "The code analysis provider returned an invalid response."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        candidates = provider_payload.get("candidates")
        if (
            not isinstance(candidates, list)
            or not candidates
            or not isinstance(candidates[0], dict)
        ):
            logger.warning("Gemini response did not contain any candidates.")
            return Response(
                {"detail": "The code analysis provider returned no analysis."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        content = candidates[0].get("content")
        if not isinstance(content, dict) or not isinstance(content.get("parts"), list):
            return Response(
                {"detail": "The code analysis provider returned an invalid response."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        parts = content["parts"]
        response_text = "".join(
            part["text"]
            for part in parts
            if isinstance(part, dict) and isinstance(part.get("text"), str)
        ).strip()
        if not response_text:
            return Response(
                {"detail": "The code analysis provider returned an empty response."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response({"response": response_text}, status=status.HTTP_200_OK)

# class ChangePasswordView(APIView):
#     def post(self, request):
#         old_password = request.data.get('old_password')
#         new_password = request.data.get('new_password')
#         user = request.user

#         if not user.check_password(old_password):
#             return Response({'detail': 'Invalid old password.'}, status=status.HTTP_400_BAD_REQUEST)

#         user.set_password(new_password)
#         user.save()
#         return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)
    

    
# # @method_decorator(csrf_protect, name='dispatch')
# class ResetPasswordEmailView(APIView):
    # permission_classes=[AllowAny]
    # def post(self, request):
    #     email = request.data.get('email')

    #     if not User.objects.filter(email=email).exists():
    #         return Response({'detail': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

    #     user = User.objects.get(email=email)

    #     # Generate password reset token
    #     uid = urlsafe_base64_encode(force_bytes(user.pk))
    #     token = default_token_generator.make_token(user)
    #     reset_link = reverse('reset_password', kwargs={'uid': uid, 'token': token})
    #     # print("Reset Link", reset_link)
    #     reset_url = f'{settings.SITE_DOMAIN}{reset_link}'
    #     # print("Reset URL", reset_url)
    #     send_reset_password_email(user.email, reset_url)

    #     return Response({'detail': 'Password reset email sent successfully.'}, status=status.HTTP_200_OK)
    
# @method_decorator(csrf_protect, name='dispatch')
# class ResetPasswordView(APIView):
#     permission_classes = [AllowAny]

# # @method_decorator(csrf_protect, name='dispatch')
# class ResetPasswordConfirmView(APIView):
#     permission_classes=[AllowAny]
#     def post(self, request):
#         uid = request.data.get('uid')
#         token = request.data.get('token')
#         if not uid or not token:
#             return Response({'detail': 'Missing uid or token.'}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             uid = force_str(urlsafe_base64_decode(uid))
#             user = User.objects.get(pk=uid)
#             if default_token_generator.check_token(user, token):
#                 new_password = request.data.get('new_password')

#                 if not new_password:
#                     return Response({'detail': 'New password is required.'}, status=status.HTTP_400_BAD_REQUEST)

#                 user.set_password(new_password)
#                 user.save()
#                 return Response({'detail': 'Password reset successful.'}, status=status.HTTP_200_OK)
#             else:
#                 return Response({'detail': 'Invalid reset password link.'}, status=status.HTTP_400_BAD_REQUEST)
#         except User.DoesNotExist:
#             return Response({'detail': 'Invalid reset password link.'}, status=status.HTTP_400_BAD_REQUEST)
