from django.urls import path
from . import views
from .api_views import GetMostRelevantAnswersView

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('add/', views.article_add, name='article_add'),
    path('<int:pk>/edit/', views.article_edit, name='article_edit'),
    path('<int:pk>/delete/', views.article_delete, name='article_delete'),
    path('upload/', views.upload_file, name='upload_file'),
    path('process_file/', views.process_file, name='process_file'),
    path('process_row/', views.process_row, name='process_row'),
    path('api/get_most_relevant_answers/', GetMostRelevantAnswersView.as_view(), name='get_most_relevant_answers'),
    path('search/', views.search, name='search'),  # Новый маршрут для поиска
    path('test_article_relevance/', views.test_article_relevance, name='test_article_relevance'),

]
