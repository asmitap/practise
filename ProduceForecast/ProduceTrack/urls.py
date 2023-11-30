from django.urls import path
from . import views
from rest_framework_simplejwt import views as jwt_views
from .views import *

urlpatterns = [
    path('', views.index, name="index"),
    path('commodity/',CommodityViewSet.as_view()),
    path('api/commodity/<int:pk>/',CommodityViewSet.as_view()),
    path('login', views.login_view, name="login_page"),
    path('api/login', UserLoginView.as_view()),
    path('logout', views.logout_view, name="logout_page"),
    path('register', views.register, name="register_page"),
    path('api/customuser/',CustomUserViewSet.as_view()),
    path('api/customuser/<int:pk>/',CustomUserViewSet.as_view()),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]