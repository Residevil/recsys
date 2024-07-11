"""
URL configuration for recsys project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.urls import include
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.IndexView.as_view(template_name = 'index.html'), name='index'),
    path('users/', views.UserIndexView.as_view(template_name = 'user_index.html'), name='user_index'),
    path('users/<int:int_id>/', views.UserDetailView.as_view(template_name = 'user_detail.html'), name='user_detail'),
    path('businesses/', views.BusinessIndexView.as_view(template_name = 'business_index.html'), name='business_index'),
    path('businesses/<int:business_id>/', views.BusinessDetailView.as_view(template_name = 'business_detail.html'), name='business_detail'),
    path('reviews/', views.ReviewIndexView.as_view(template_name = 'review_index.html'), name='review_index'),
    path('reviews/<int:review_id>/', views.ReviewDetailView.as_view(template_name = 'review_detail'), name='review_detail'),
    path('demo/yelp-businesses', views.demo_yelp_business),
    path('demo/yelp-business-detail/<slug:business_id>/', views.demo_yelp_business_detail),
    path('demo/yelp-business-reviews/<slug:business_id>/', views.demo_yelp_business_reviews),
    path('dump-yelp-data/', views.dump_yelp_data),
    # path("accounts/", include("django.contrib.auth.urls")),
    path("login/", views.MyLoginView.as_view(next_page="/reviewmaster/index.html", template_name="registration/login.html"), name='login'),
    path("logout/", views.MyLogoutView.as_view(template_name="registration/logout.html"), name='logout'),
    path("password_reset/", auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"), name='password_reset'),
    path("password_reset_done/", auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), name='password_reset_done'),
    path("password_reset_confirm/", auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), name='password_reset_confirm'),
    path("password_reset_complete/", auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), name='password_reset_complete'),
    
    # path("login/", views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # path("logout/", views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path("register/", views.RegisterView.as_view(template_name="registration/register.html"), name='register'),
    # path("password-reset/", views.PasswordResetView.as_view(template_name="registration/password_reset.html"), name='password_reset'),
    # path("password-reset-done/", views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), name='password_reset_done'),
    # path("change-password/", views.PasswordChangeView.as_view(template_name="registration/password_change.html"), name="password_change"),

    path("generate/", views.GenerateRandomUserView.as_view(template_name="reviewmaster/generate_random_users.html"), name="generate_random_users"),
    path("search/", views.SearchResultView.as_view(template_name="reviewmaster/search_result.html"), name="search_result"),
]
