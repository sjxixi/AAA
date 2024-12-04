from django.urls import path
from . import views
from .views.devices import (
    ServerView, NetworkDeviceView, StorageDeviceView, SecurityDeviceView
)

app_name = 'assets'

urlpatterns = [
    # 数据中心URLs
    path('', views.dashboard, name='dashboard'),
    path('datacenter/', views.datacenter_list, name='datacenter_list'),
    path('datacenter/create/', views.datacenter_create, name='datacenter_create'),
    path('datacenter/<int:pk>/', views.datacenter_detail, name='datacenter_detail'),
    path('datacenter/<int:pk>/edit/', views.datacenter_edit, name='datacenter_edit'),
    path('datacenter/<int:pk>/delete/', views.datacenter_delete, name='datacenter_delete'),
    path('datacenter/<int:pk>/history/', views.datacenter_history, name='datacenter_history'),

    # 服务器URLs
    path('server/', ServerView.as_view(), name='server_list'),
    path('server/create/', ServerView.as_view(), name='server_create'),
    path('server/<int:pk>/', ServerView.as_view(), name='server_detail'),
    path('server/<int:pk>/edit/', ServerView.as_view(), name='server_edit'),
    path('server/<int:pk>/delete/', ServerView.as_view(), name='server_delete'),
    path('server/<int:pk>/history/', ServerView.as_view(), name='server_history'),

    # 网络设备URLs
    path('network/', NetworkDeviceView.as_view(), name='network_list'),
    path('network/create/', NetworkDeviceView.as_view(), name='network_create'),
    path('network/<int:pk>/', NetworkDeviceView.as_view(), name='network_detail'),
    path('network/<int:pk>/edit/', NetworkDeviceView.as_view(), name='network_edit'),
    path('network/<int:pk>/delete/', NetworkDeviceView.as_view(), name='network_delete'),
    path('network/<int:pk>/history/', NetworkDeviceView.as_view(), name='network_history'),

    # 存储设备URLs
    path('storage/', StorageDeviceView.as_view(), name='storage_list'),
    path('storage/create/', StorageDeviceView.as_view(), name='storage_create'),
    path('storage/<int:pk>/', StorageDeviceView.as_view(), name='storage_detail'),
    path('storage/<int:pk>/edit/', StorageDeviceView.as_view(), name='storage_edit'),
    path('storage/<int:pk>/delete/', StorageDeviceView.as_view(), name='storage_delete'),
    path('storage/<int:pk>/history/', StorageDeviceView.as_view(), name='storage_history'),

    # 安全设备URLs
    path('security/', SecurityDeviceView.as_view(), name='security_list'),
    path('security/create/', SecurityDeviceView.as_view(), name='security_create'),
    path('security/<int:pk>/', SecurityDeviceView.as_view(), name='security_detail'),
    path('security/<int:pk>/edit/', SecurityDeviceView.as_view(), name='security_edit'),
    path('security/<int:pk>/delete/', SecurityDeviceView.as_view(), name='security_delete'),
    path('security/<int:pk>/history/', SecurityDeviceView.as_view(), name='security_history'),
] 