from django.contrib import admin
from django.urls import path, include
from themes import views as themes_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', themes_views.home, name='home'),
    path('themes/', include('themes.urls')),
    path('register/', themes_views.register, name='register'),
    path('login/', themes_views.login_view, name='login'),
    path('logout/', themes_views.logout_view, name='logout'),  # Обновляем URL для выхода
    path('profile/', themes_views.profile, name='profile'),
    path('regenerate_api_key/', themes_views.regenerate_api_key, name='regenerate_api_key'),
]
