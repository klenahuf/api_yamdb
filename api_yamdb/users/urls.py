from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenVerifyView)


router = DefaultRouter()

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup', include('djoser.urls')),
    path(
        'v1/jwt/create/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path('v1/jwt/verify/', TokenVerifyView.as_view(), name='token_verify')
]
