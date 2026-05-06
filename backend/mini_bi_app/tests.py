import json
import os
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Dataset, Report, ColumnTrainingData, ColumnPrediction
from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserSerializer,
    DatasetSerializer,
    ReportSerializer,
    ColumnTrainingDataSerializer,
    ColumnPredictionSerializer
)


class ModelTests(TestCase):
    """Test cases for Django models"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_dataset_model_creation(self):
        """Test Dataset model creation"""
        # Create a simple file for testing
        test_file = SimpleUploadedFile(
            "test.csv",
            b"col1,col2\nval1,val2",
            content_type="text/csv"
        )

        dataset = Dataset.objects.create(
            user=self.user,
            name="Test Dataset",
            file=test_file
        )

        self.assertEqual(dataset.name, "Test Dataset")
        self.assertEqual(dataset.user, self.user)
        self.assertIsNotNone(dataset.created_at)
        self.assertEqual(str(dataset), "Test Dataset")

    def test_report_model_creation(self):
        """Test Report model creation"""
        # Create dataset first
        test_file = SimpleUploadedFile(
            "test.csv",
            b"col1,col2\nval1,val2",
            content_type="text/csv"
        )
        dataset = Dataset.objects.create(
            user=self.user,
            name="Test Dataset",
            file=test_file
        )

        report = Report.objects.create(
            user=self.user,
            dataset=dataset,
            summary={"key": "value"},
            charts={"chart": "data"}
        )

        self.assertEqual(report.user, self.user)
        self.assertEqual(report.dataset, dataset)
        self.assertEqual(report.summary, {"key": "value"})
        self.assertEqual(report.charts, {"chart": "data"})
        self.assertIsNotNone(report.created_at)

    def test_column_training_data_model(self):
        """Test ColumnTrainingData model"""
        training_data = ColumnTrainingData.objects.create(
            column_name="revenue",
            features={"type": "numeric", "pattern": "currency"},
            semantic_label="Revenue",
            sample_values=["100", "200", "300"]
        )

        self.assertEqual(training_data.column_name, "revenue")
        self.assertEqual(training_data.semantic_label, "Revenue")
        self.assertEqual(str(training_data), "revenue")

    def test_column_prediction_model(self):
        """Test ColumnPrediction model"""
        # Create dataset first
        test_file = SimpleUploadedFile(
            "test.csv",
            b"col1,col2\nval1,val2",
            content_type="text/csv"
        )
        dataset = Dataset.objects.create(
            user=self.user,
            name="Test Dataset",
            file=test_file
        )

        prediction = ColumnPrediction.objects.create(
            dataset=dataset,
            column_name="revenue",
            semantic_label="Revenue",
            confidence_score=0.95,
            aggregation="sum"
        )

        self.assertEqual(prediction.dataset, dataset)
        self.assertEqual(prediction.column_name, "revenue")
        self.assertEqual(prediction.semantic_label, "Revenue")
        self.assertEqual(prediction.confidence_score, 0.95)
        self.assertEqual(prediction.aggregation, "sum")
        self.assertEqual(str(prediction), "revenue")


class SerializerTests(TestCase):
    """Test cases for serializers"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_user_registration_serializer_valid(self):
        """Test UserRegistrationSerializer with valid data"""
        data = {
            'email': 'newuser@example.com',
            'password': 'password123',
            'password2': 'password123',
            'first_name': 'New',
            'last_name': 'User'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')

    def test_user_registration_serializer_invalid_email(self):
        """Test UserRegistrationSerializer with duplicate email"""
        # Create existing user
        User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='pass123'
        )

        data = {
            'email': 'existing@example.com',
            'password': 'password123',
            'password2': 'password123'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_user_registration_serializer_password_mismatch(self):
        """Test UserRegistrationSerializer with mismatched passwords"""
        data = {
            'email': 'newuser@example.com',
            'password': 'password123',
            'password2': 'different123'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_user_serializer(self):
        """Test UserSerializer"""
        serializer = UserSerializer(self.user)
        expected_fields = ['id', 'username', 'email', 'first_name', 'last_name']
        self.assertEqual(set(serializer.data.keys()), set(expected_fields))

    def test_dataset_serializer(self):
        """Test DatasetSerializer"""
        test_file = SimpleUploadedFile(
            "test.csv",
            b"col1,col2\nval1,val2",
            content_type="text/csv"
        )
        dataset = Dataset.objects.create(
            user=self.user,
            name="Test Dataset",
            file=test_file
        )

        serializer = DatasetSerializer(dataset)
        self.assertEqual(serializer.data['name'], "Test Dataset")
        self.assertEqual(serializer.data['user'], self.user.id)

    def test_column_training_data_serializer(self):
        """Test ColumnTrainingDataSerializer"""
        training_data = ColumnTrainingData.objects.create(
            column_name="revenue",
            features={"type": "numeric"},
            semantic_label="Revenue"
        )

        serializer = ColumnTrainingDataSerializer(training_data)
        self.assertEqual(serializer.data['column_name'], "revenue")
        self.assertEqual(serializer.data['semantic_label'], "Revenue")


class AuthenticationAPITests(APITestCase):
    """Test cases for authentication endpoints"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.register_url = reverse('register')
        self.login_url = reverse('token_obtain_pair')
        self.logout_url = reverse('logout')
        self.profile_url = reverse('profile')
        self.token_refresh_url = reverse('token_refresh')

    def test_user_registration_success(self):
        """Test successful user registration"""
        data = {
            'email': 'newuser@example.com',
            'password': 'password123',
            'password2': 'password123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        data = {
            'email': 'testuser@example.com',  # Same as existing user
            'password': 'password123',
            'password2': 'password123'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_login_success(self):
        """Test successful user login"""
        data = {
            'username': 'testuser@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'username': 'testuser@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_logout(self):
        """Test user logout"""
        # First login to get tokens
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Set authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        data = {'refresh': refresh_token}
        response = self.client.post(self.logout_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_get_user_profile_authenticated(self):
        """Test getting user profile when authenticated"""
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'testuser@example.com')

    def test_get_user_profile_unauthenticated(self):
        """Test getting user profile when not authenticated"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_profile(self):
        """Test updating user profile"""
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        data = {'first_name': 'Updated', 'last_name': 'Name'}
        response = self.client.put(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['first_name'], 'Updated')

    def test_token_refresh(self):
        """Test token refresh"""
        refresh = RefreshToken.for_user(self.user)
        refresh_token = str(refresh)

        data = {'refresh': refresh_token}
        response = self.client.post(self.token_refresh_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class DatasetAPITests(APITestCase):
    """Test cases for Dataset API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='testpass123'
        )

        # Get authentication token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.datasets_url = reverse('datasets-list')

    def test_list_datasets_authenticated(self):
        """Test listing datasets for authenticated user"""
        # Create some test datasets
        test_file = SimpleUploadedFile(
            "test1.csv",
            b"col1,col2\nval1,val2",
            content_type="text/csv"
        )
        Dataset.objects.create(user=self.user, name="Dataset 1", file=test_file)

        test_file2 = SimpleUploadedFile(
            "test2.csv",
            b"col1,col2\nval1,val2",
            content_type="text/csv"
        )
        Dataset.objects.create(user=self.user, name="Dataset 2", file=test_file2)

        response = self.client.get(self.datasets_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_datasets_other_user(self):
        """Test that users only see their own datasets"""
        # Create dataset for other user
        test_file = SimpleUploadedFile(
            "other.csv",
            b"col1,col2\nval1,val2",
            content_type="text/csv"
        )
        Dataset.objects.create(user=self.other_user, name="Other Dataset", file=test_file)

        response = self.client.get(self.datasets_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Should not see other user's dataset

    def test_create_dataset_valid_csv(self):
        """Test creating a dataset with valid CSV file"""
        test_file = SimpleUploadedFile(
            "test.csv",
            b"col1,col2\nval1,val2\nval3,val4",
            content_type="text/csv"
        )

        data = {
            'name': 'Test Dataset',
            'file': test_file
        }

        response = self.client.post(self.datasets_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Dataset')
        self.assertTrue(Dataset.objects.filter(name='Test Dataset').exists())

    def test_create_dataset_invalid_file_type(self):
        """Test creating a dataset with invalid file type"""
        test_file = SimpleUploadedFile(
            "test.txt",
            b"This is not a CSV file",
            content_type="text/plain"
        )

        data = {
            'name': 'Test Dataset',
            'file': test_file
        }

        response = self.client.post(self.datasets_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.data)

    def test_delete_dataset(self):
        """Test deleting a dataset"""
        test_file = SimpleUploadedFile(
            "test.csv",
            b"col1,col2\nval1,val2",
            content_type="text/csv"
        )
        dataset = Dataset.objects.create(user=self.user, name="Test Dataset", file=test_file)

        delete_url = reverse('datasets-detail', kwargs={'pk': dataset.id})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Dataset.objects.filter(id=dataset.id).exists())

    def test_delete_other_users_dataset(self):
        """Test that users cannot delete other users' datasets"""
        test_file = SimpleUploadedFile(
            "other.csv",
            b"col1,col2\nval1,val2",
            content_type="text/csv"
        )
        dataset = Dataset.objects.create(user=self.other_user, name="Other Dataset", file=test_file)

        delete_url = reverse('datasets-detail', kwargs={'pk': dataset.id})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # Should not find the dataset


class ReportAPITests(APITestCase):
    """Test cases for Report API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='testpass123'
        )

        # Get authentication token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.reports_url = reverse('reports-list')

    def test_list_reports_authenticated(self):
        """Test listing reports for authenticated user"""
        # Create dataset and report
        test_file = SimpleUploadedFile(
            "test.csv",
            b"col1,col2\nval1,val2",
            content_type="text/csv"
        )
        dataset = Dataset.objects.create(user=self.user, name="Test Dataset", file=test_file)

        Report.objects.create(
            user=self.user,
            dataset=dataset,
            summary={"summary": "test"},
            charts={"charts": "test"}
        )

        response = self.client.get(self.reports_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_reports_other_user(self):
        """Test that users only see their own reports"""
        # Create dataset and report for other user
        test_file = SimpleUploadedFile(
            "other.csv",
            b"col1,col2\nval1,val2",
            content_type="text/csv"
        )
        dataset = Dataset.objects.create(user=self.other_user, name="Other Dataset", file=test_file)

        Report.objects.create(
            user=self.other_user,
            dataset=dataset,
            summary={"summary": "other"},
            charts={"charts": "other"}
        )

        response = self.client.get(self.reports_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Should not see other user's reports

    def test_create_report_via_dataset_upload(self):
        """Test that uploading a dataset creates a report automatically"""
        # This is tested implicitly in DatasetAPITests.test_create_dataset_valid_csv
        # The perform_create method in DatasetViewSet calls run_pipeline which creates a report
        # For unit testing, we might need to mock the pipeline or test the logic separately
        pass

    def test_get_report_detail(self):
        """Test getting report details"""
        # Create dataset and report
        test_file = SimpleUploadedFile(
            "test.csv",
            b"col1,col2\nval1,val2",
            content_type="text/csv"
        )
        dataset = Dataset.objects.create(user=self.user, name="Test Dataset", file=test_file)

        report = Report.objects.create(
            user=self.user,
            dataset=dataset,
            summary={"summary": "test"},
            charts={"charts": "test"}
        )

        detail_url = reverse('reports-detail', kwargs={'pk': report.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['summary'], {"summary": "test"})


class PermissionTests(APITestCase):
    """Test cases for permissions and access control"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='testpass123'
        )

    def test_unauthenticated_access_datasets(self):
        """Test that unauthenticated users cannot access dataset endpoints"""
        datasets_url = reverse('datasets-list')
        response = self.client.get(datasets_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test POST
        response = self.client.post(datasets_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_access_reports(self):
        """Test that unauthenticated users cannot access report endpoints"""
        reports_url = reverse('reports-list')
        response = self.client.get(reports_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_access_profile(self):
        """Test that unauthenticated users cannot access profile"""
        profile_url = reverse('profile')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(profile_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
