from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Dataset, Report, ColumnTrainingData, ColumnPrediction
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserSerializer,
    DatasetSerializer,
    ReportSerializer
)
import os
from .ai_pipeline.pipeline import run_pipeline


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    
    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {
                    "access": serializer.validated_data['access'],
                    "refresh": serializer.validated_data['refresh']
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logged out successfully"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Profile updated successfully", "user": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DatasetViewSet(ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        print("Getting datasets for user:", self.request)
        return Dataset.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        print("Creating dataset for user:", self.request.user)
        instance = serializer.save(user=self.request.user)
        
        file_path = instance.file.path
        print("File path:", file_path)
        

        if file_path.endswith('.csv') or file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            print("File type is valid, proceeding with classification.")

            report = run_pipeline(file_path, dataset_instance=instance)
            print("Report created with ID:", report.id)
            serializer = ReportSerializer(report)
            print("Report summary:", serializer.data['summary'])
            # Here you would add the logic to read the file and classify columns
            # For example:
            # df = pd.read_csv(file_path) or pd.read_excel(file_path)
            # profiles = classify_columns(df)
        else:
            print("Unsupported file type:", file_path)
            instance.delete()  # Clean up the uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"File deleted: {file_path}")
            raise ValidationError({
                "file": "Unsupported file type. Please upload a CSV or Excel file (.csv, .xlsx, .xls)."
            })

    def perform_destroy(self, instance):
        """Delete both the database instance and the actual file from filesystem"""
        # Get file path before deleting the instance
        if instance.file:
            file_path = instance.file.path
            # Delete the instance first
            instance.delete()
            # Then delete the actual file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"File deleted: {file_path}")
        else:
            instance.delete()