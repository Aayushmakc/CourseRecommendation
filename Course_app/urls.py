from django.urls import path
from .views import SignupView, LoginView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import CourseSearchView


urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('search/', CourseSearchView.as_view(), name='course-search'),

]
    

