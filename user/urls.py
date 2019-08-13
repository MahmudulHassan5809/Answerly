from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
import user.views as views

app_name = 'user'

urlpatterns = [
	path('register',views.RegisterView.as_view(),name='register'),
	path('login',LoginView.as_view(),name='login'),
	path('logout',LogoutView.as_view(),name='logout'),
]
