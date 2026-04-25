from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    DatasetViewSet,
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView
)

router = DefaultRouter()
router.register(r'datasets', DatasetViewSet, basename='datasets')

urlpatterns = [
    path('', include(router.urls)),  # ✅ include router
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]