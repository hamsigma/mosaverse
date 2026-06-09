"""
MosaVerse Automated Tests

Run with: python manage.py test
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.designs.models import Category, Design
from rest_framework.test import APIClient
import json


class CategoryModelTest(TestCase):
    """Test Category model."""

    def test_create_category(self):
        cat = Category.objects.create(name='Casual')
        self.assertEqual(cat.name, 'Casual')
        self.assertEqual(cat.slug, 'casual')
        self.assertEqual(str(cat), 'Casual')

    def test_unique_name(self):
        Category.objects.create(name='Casual')
        with self.assertRaises(Exception):
            Category.objects.create(name='Casual')


class DesignModelTest(TestCase):
    """Test Design model."""

    def setUp(self):
        self.category = Category.objects.create(name='Streetwear')

    def test_create_design(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        image = SimpleUploadedFile(
            "test.jpg",
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b",
            content_type="image/jpeg"
        )
        design = Design.objects.create(
            title='Test Design',
            description='A test design',
            image=image,
            category=self.category,
        )
        self.assertEqual(design.title, 'Test Design')
        self.assertEqual(design.slug, 'test-design')
        self.assertEqual(design.category, self.category)
        self.assertTrue(design.is_published)
        self.assertFalse(design.is_featured)


class APIEndpointsTest(TestCase):
    """Test all API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            'testadmin', 'test@test.com', 'testpass123')
        self.category = Category.objects.create(name='Formal')

    def test_designs_list_public(self):
        response = self.client.get('/api/designs/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)

    def test_categories_list_public(self):
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post('/api/login/', {
            'username': 'testadmin',
            'password': 'testpass123'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('user', response.data)
        self.assertTrue(response.data['user']['is_staff'])

    def test_login_fail(self):
        response = self.client.post('/api/login/', {
            'username': 'wrong',
            'password': 'wrong'
        }, format='json')
        self.assertEqual(response.status_code, 401)

    def test_login_missing_fields(self):
        response = self.client.post('/api/login/', {}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_me_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testadmin')

    def test_me_unauthenticated(self):
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, 403)

    def test_dashboard_requires_admin(self):
        response = self.client.get('/api/dashboard/stats/')
        self.assertEqual(response.status_code, 403)

    def test_dashboard_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/dashboard/stats/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('stats', response.data)

    def test_ai_search_missing_query(self):
        response = self.client.post('/api/ai/search/', {}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_ai_search_short_query(self):
        response = self.client.post(
            '/api/ai/search/', {'query': 'ab'}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_generate_description_requires_auth(self):
        response = self.client.post('/api/ai/generate-description/', {
            'title': 'Test'
        }, format='json')
        self.assertEqual(response.status_code, 403)

    def test_generate_description_requires_title(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            '/api/ai/generate-description/', {}, format='json')
        self.assertEqual(response.status_code, 400)


class SecurityTest(TestCase):
    """Test security features."""

    def setUp(self):
        self.client = Client()

    def test_security_headers_present(self):
        response = self.client.get('/api/designs/')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertIn('X-XSS-Protection', response)
        self.assertIn('Referrer-Policy', response)

    def test_xframe_options(self):
        response = self.client.get('/api/designs/')
        self.assertEqual(response['X-Frame-Options'], 'DENY')


class PerformanceTest(TestCase):
    """Basic performance tests."""

    def setUp(self):
        self.client = APIClient()
        # Create test data
        cat = Category.objects.create(name='Test')
        from django.core.files.uploadedfile import SimpleUploadedFile
        image = SimpleUploadedFile(
            "test.jpg",
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b",
            content_type="image/jpeg"
        )
        for i in range(20):
            Design.objects.create(
                title=f'Design {i}',
                description=f'Description {i}',
                image=image,
                category=cat,
            )

    def test_designs_list_response_time(self):
        """Designs list should respond within 3 seconds."""
        import time
        start = time.time()
        response = self.client.get('/api/designs/')
        elapsed = time.time() - start
        self.assertEqual(response.status_code, 200)
        self.assertLess(
            elapsed, 3.0, f"Response took {elapsed:.2f}s (limit: 3s)")

    def test_designs_pagination(self):
        """Should return paginated results."""
        response = self.client.get('/api/designs/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 20)
        self.assertEqual(len(response.data['results']), 12)  # PAGE_SIZE
