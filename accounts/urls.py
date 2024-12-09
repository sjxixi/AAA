from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:pk>/permissions/', views.user_permissions, name='user_permissions'),
    path('user/<int:user_id>/change-password/', views.change_password, name='change_password'),
] 