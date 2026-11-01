import json
import os
import zlib
from io import StringIO
from unittest.mock import Mock, patch

from django.contrib.auth.tokens import default_token_generator
from django.test import override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate
from rest_framework_simplejwt.tokens import AccessToken

from account.models import Report, User
from account.views import CodeAnalysisView, CodeExecutionView


class AccountAndReportApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="owner@example.com",
            name="Report Owner",
            password="test-password-123",
        )
        self.user.is_active = True
        self.user.save()
        self.other_user = User.objects.create_user(
            email="other@example.com",
            name="Other User",
            password="test-password-123",
        )
        self.other_user.is_active = True
        self.other_user.save()
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.user)}"
        )

    def test_report_is_assigned_to_authenticated_user_and_scoped(self):
        response = self.client.post(
            reverse("report"),
            {
                "user": self.other_user.id,
                "title": "Potential bug",
                "bug_code": "print('example')",
                "bug_report": "No issue found.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        report = Report.objects.get()
        self.assertEqual(report.user, self.user)
        self.assertEqual(response.data["data"]["user"], self.user.id)

        Report.objects.create(
            user=self.other_user,
            title="Another user's report",
            bug_code="x = 1",
            bug_report="Private report.",
        )
        list_response = self.client.get(reverse("report"))
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data["data"]), 1)
        self.assertEqual(list_response.data["data"][0]["title"], "Potential bug")

    def test_report_requires_authentication(self):
        self.client.credentials()
        response = self.client.get(reverse("report"))
        self.assertEqual(response.status_code, 401)

    def test_health_endpoint_checks_database(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "ok"})

    def test_active_user_can_sign_in_and_receive_jwt(self):
        self.client.credentials()
        response = self.client.post(
            reverse("login"),
            {
                "email": self.user.email,
                "password": "test-password-123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data["token2"])
        self.assertIn("refresh", response.data["token2"])

    @override_settings(GEMINI_API_KEY="")
    def test_analysis_reports_missing_server_configuration(self):
        request = APIRequestFactory().post(
            reverse("code_analysis"),
            {"prompt": "Explain this code."},
            format="json",
        )
        force_authenticate(request, user=self.user)
        response = CodeAnalysisView.as_view()(request)
        self.assertEqual(response.status_code, 503)
        self.assertIn("GEMINI_API_KEY", response.data["detail"])

    @override_settings(GEMINI_API_KEY="test-key")
    @patch("account.views.urlopen")
    def test_analysis_calls_provider_from_backend(self, mocked_urlopen):
        provider_response = Mock()
        provider_response.__enter__ = Mock(return_value=provider_response)
        provider_response.__exit__ = Mock(return_value=False)
        provider_response.read.return_value = json.dumps(
            {
                "candidates": [
                    {"content": {"parts": [{"text": "No bugs found."}]}}
                ]
            }
        ).encode("utf-8")
        mocked_urlopen.return_value = provider_response

        response = self.client.post(
            reverse("code_analysis"),
            {"prompt": "Analyze this sample."},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["response"], "No bugs found.")
        provider_request = mocked_urlopen.call_args.args[0]
        self.assertNotIn("test-key", provider_request.full_url)
        self.assertEqual(provider_request.get_header("X-goog-api-key"), "test-key")

    @patch("account.views.urlopen")
    def test_code_execution_uses_sandboxed_runner(self, mocked_urlopen):
        provider_response = Mock()
        provider_response.__enter__ = Mock(return_value=provider_response)
        provider_response.__exit__ = Mock(return_value=False)
        token = "1234567890abcdef"
        provider_response.read.return_value = (
            f"{token}\n{token}\n2\nExit code: 0{token}".encode("utf-8")
        )
        mocked_urlopen.return_value = provider_response

        response = self.client.post(
            reverse("code_execution"),
            {
                "language": "python",
                "code": "print(1 + 1)",
                "input": "",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["exit_code"], 0)
        self.assertIn("2", response.data["output"])
        provider_request = mocked_urlopen.call_args.args[0]
        payload = zlib.decompress(provider_request.data, wbits=-zlib.MAX_WBITS)
        self.assertIn(b"python3", payload)
        self.assertIn(b"print(1 + 1)", payload)
        self.assertEqual(provider_request.full_url, "https://tio.run/cgi-bin/run/api/")

    @patch("account.views.urlopen")
    def test_code_execution_rejects_unsupported_language(self, mocked_urlopen):
        response = self.client.post(
            reverse("code_execution"),
            {"language": "bash", "code": "echo unsafe"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        mocked_urlopen.assert_not_called()


class RegistrationApiTests(APITestCase):
    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
        EMAIL_HOST_USER="",
        EMAIL_HOST_PASSWORD="",
    )
    def test_registration_returns_configuration_error_without_creating_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "name": "New User",
                "email": "new-user@example.com",
                "password": "valid-password-123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 503)
        self.assertFalse(User.objects.filter(email="new-user@example.com").exists())

    @override_settings(
        AUTO_ACTIVATE_SIGNUPS=True,
        EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
        EMAIL_HOST_USER="",
        EMAIL_HOST_PASSWORD="",
    )
    @patch("account.views.send_activation_email")
    def test_registration_activates_without_smtp_when_configured(
        self, send_activation_email
    ):
        response = self.client.post(
            reverse("register"),
            {
                "name": "New User",
                "email": "new-user@example.com",
                "password": "valid-password-123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["activated"])
        user = User.objects.get(email="new-user@example.com")
        self.assertTrue(user.is_active)
        send_activation_email.assert_not_called()
        login_response = self.client.post(
            reverse("login"),
            {
                "email": "new-user@example.com",
                "password": "valid-password-123",
            },
            format="json",
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access", login_response.data["token2"])

    @patch("account.views.send_activation_email")
    def test_registration_creates_inactive_user_and_sends_activation_email(
        self, send_activation_email
    ):
        response = self.client.post(
            reverse("register"),
            {
                "name": "New User",
                "email": "new-user@example.com",
                "password": "valid-password-123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email="new-user@example.com")
        self.assertFalse(user.is_active)
        send_activation_email.assert_called_once()
        self.assertEqual(send_activation_email.call_args.args[0], user.email)
        self.assertIn("/api/account/activate/", send_activation_email.call_args.args[1])
        self.assertNotIn("token2", response.data)

    def test_activation_redirects_to_the_hash_router_landing_page(self):
        user = User.objects.create_user(
            email="activate@example.com",
            name="Activate User",
            password="test-password-123",
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.get(
            reverse("activate", kwargs={"uid": uid, "token": token})
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            "http://localhost:3000/#/?message=Account+Successfully+Activated",
        )
        user.refresh_from_db()
        self.assertTrue(user.is_active)


class DemoAccountCommandTests(APITestCase):
    @patch.dict(
        os.environ,
        {
            "BUGSFINDER_DEMO_EMAIL": "demo@example.com",
            "BUGSFINDER_DEMO_PASSWORD": "safe-demo-password-2026",
        },
    )
    def test_command_creates_active_login_account(self):
        from django.core.management import call_command

        call_command("create_demo_user", stdout=StringIO())

        user = User.objects.get(email="demo@example.com")
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password("safe-demo-password-2026"))

    @patch.dict(os.environ, {}, clear=True)
    def test_command_skips_when_demo_credentials_are_not_configured(self):
        from django.core.management import call_command

        call_command("create_demo_user", stdout=StringIO())

        self.assertFalse(User.objects.filter(email="demo@example.com").exists())
