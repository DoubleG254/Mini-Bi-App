from .models import ColumnPrediction,ColumnTrainingData,Report,Dataset
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 'last_name']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        email = validated_data['email']
        # Use email as both username and email
        user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer that accepts email as username for login
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')  # This will be the email
        password = attrs.get('password')

        # Try to authenticate with email as username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": "No account found with the given email"}
            )

        # Verify password
        if not user.check_password(password):
            raise serializers.ValidationError(
                {"detail": "Incorrect password"}
            )

        # Check if user is active
        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": "This account is inactive"}
            )

        # Get tokens
        refresh = self.get_token(user)
        attrs['refresh'] = str(refresh)
        attrs['access'] = str(refresh.access_token)

        return attrs

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['first_name'] = user.first_name
        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class DatasetSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True
    )


    class Meta:
        model = Dataset
        fields = ['id', 'user', 'name', 'file', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']  # Make user read-only if view handles it

    def create(self, validated_data):
        # Remove the manual assignment; let the view handle it via serializer.save(user=...)
        return super().create(validated_data)


# Report Serializer
class ReportSerializer(serializers.ModelSerializer):
    file =serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    user = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
  

    class Meta:
        model = Report
        fields = ['id', 'user','file', 'summary', 'charts', 'created_at']
        read_only_fields = ['id', 'created_at']


# ColumnTrainingData Serializer
class ColumnTrainingDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColumnTrainingData
        fields = ['id', 'column_name', 'features', 'semantic_label', 'aggregation']


# ColumnPrediction Serializer
class ColumnPredictionSerializer(serializers.ModelSerializer):
    file = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
 

    class Meta:
        model = ColumnPrediction
        fields = [
            'id',
            'file',
            'column_name',
            'semantic_label',
            'confidence_score',
            'aggregation'
        ]

