INSTALLED_APPS = [
    ...
    'accounts',
    ...
] 

# 设备状态配置
DEVICE_STATUS = {
    'running': '运行中',
    'stopped': '已停止',
    'maintenance': '维护中',
    'fault': '故障'
} 

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
} 