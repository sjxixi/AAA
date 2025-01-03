"""
Django settings for AAA project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6w9_su48x&$f6(lw1!9d%efpspsv*^^*7q8&k4v_)=99$%()*2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'accounts.apps.AccountsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'assets.apps.AssetsConfig',
    'django_filters',
    'import_export',
    'simple_history',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'AAA.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'AAA.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cmdb',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': '192.168.117.12',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4'
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': ('username', 'email'),
            'max_similarity': 0.7,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/login/'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

SIMPLE_HISTORY_HISTORY_CHANGE_REASON_USE_TEXT_FIELD = True

# 添加设备管理相关的配置
DEVICE_TYPES = {
    'server': '服务器',
    'network': '网络设备',
    'storage': '存储设备',
    'security': '安全设备',
}

# 设备状态选项
DEVICE_STATUS = {
    'running': '运行中',
    'stopped': '已停止',
    'maintenance': '维护中',
    'fault': '故障',
}

# 分页配置
PAGINATION_PAGE_SIZE = 10

# 文件上传配置
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 测试配置
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# 会话配置
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 两周，单位秒
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_SECURE = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True

# 记住密码时间(单位:秒)
REMEMBER_ME_DURATION = 1209600  # 两周

# 登录尝试限制
MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_TIMEOUT = 300  # 5分钟

# 添加权限组配置
GROUPS = {
    'admin': ['view', 'add', 'change', 'delete', 'export'],
    'operator': ['view', 'change'],
    'viewer': ['view']
}

# 添加权限映射
PERMISSIONS = {
    'view': '查看',
    'add': '添加',
    'change': '修改', 
    'delete': '删除',
    'export': '导出'
}

# 导入导出配置
IMPORT_EXPORT_USE_TRANSACTIONS = True
IMPORT_EXPORT_SKIP_ADMIN_LOG = False

# 文件上传配置
IMPORT_EXPORT_TMP_STORAGE_CLASS = 'import_export.tmp_storages.TempFolderStorage'
IMPORT_EXPORT_IMPORT_PERMISSION_CODE = 'add'
IMPORT_EXPORT_EXPORT_PERMISSION_CODE = 'view'

# 导入导出格式
IMPORT_EXPORT_FORMATS = [
    'xlsx',
    'xls',
    'csv',
]

# 导入导出字段映射
IMPORT_EXPORT_FIELD_MAPPINGS = {
    'status': {
        'running': '运行中',
        'stopped': '已停止',
        'maintenance': '维护中',
        'fault': '故障'
    }
}

# 导入导出错误信息
IMPORT_EXPORT_ERROR_MESSAGES = {
    'required': '此字段为必填项',
    'invalid': '无效的值',
    'unique': '此值已存在',
    'foreign_key': '无效的外键值'
}

# 导入导出日志配置
IMPORT_EXPORT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'import_export.log',
        },
    },
    'loggers': {
        'import_export': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True
        },
    }
}

# 指定自定义用户模型
AUTH_USER_MODEL = 'accounts.User'
