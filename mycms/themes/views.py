import json
import logging
import os
from io import StringIO

import numpy as np
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

from .api_views import get_embeddings, cosine_similarity
from .forms import UserRegisterForm


@login_required
def article_list(request):
    articles = Article.objects.filter(user=request.user).order_by('-article_id')
    paginator = Paginator(articles, 15)  # Показывать 10 статей на страницу

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'themes/article_list.html', {'page_obj': page_obj})
@login_required
def article_add(request):
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.user = request.user
            article.save()  # Вызовется метод save модели, который заполнит поле vector
            return redirect('article_list')
    else:
        form = ArticleForm()
    return render(request, 'themes/article_form.html', {'form': form})


@login_required
def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk, user=request.user)
    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            article.save()  # Вызовется метод save модели, который заполнит поле vector
            return redirect('article_list')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'themes/article_form.html', {'form': form})


@login_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk, user=request.user)
    if request.method == "POST":
        article.delete()
        messages.success(request, 'Article deleted successfully.')
        return redirect('article_list')
    return render(request, 'themes/article_confirm_delete.html', {'article': article})


from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm


def home(request):
    if request.user.is_authenticated:
        return redirect('article_list')
    else:
        return redirect('login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('article_list')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'You are now logged in as {username}.')
                return redirect('article_list')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'themes/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have successfully logged out.')
        return redirect('home')
    return render(request, 'themes/logout.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'themes/register.html', {'form': form})


@login_required
def profile(request):
    user_profile = request.user.profile
    return render(request, 'themes/profile.html', {'user_profile': user_profile})


@login_required
def regenerate_api_key(request):
    user_profile = request.user.profile
    user_profile.api_key = user_profile.generate_api_key()
    user_profile.save()
    return redirect('profile')


import csv
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Article
from .forms import UploadFileForm, ArticleForm

logger = logging.getLogger(__name__)


def get_row_count(file_data):
    file_stream = StringIO(file_data)
    reader = csv.reader(file_stream)
    row_count = sum(1 for row in reader)
    return row_count


@login_required
def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            file_data = file.read().decode('utf-8')
            row_count = get_row_count(file_data)
            # Сохраняем данные файла в сессии
            request.session['file_data'] = file_data
            request.session['total_rows'] = row_count - 1  # Минус один для пропуска заголовка
            request.session['processed_rows'] = 0
            return redirect('process_file')
    else:
        form = UploadFileForm()
    return render(request, 'themes/upload_file.html', {'form': form})


@login_required
def process_file(request):
    total_rows = request.session.get('total_rows', 0)
    return render(request, 'themes/process_file.html', {'total_rows': total_rows})


@login_required
@csrf_exempt
def process_row(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        file_data = request.session.get('file_data', "")
        processed_rows = request.session.get('processed_rows', 0)
        total_rows = request.session.get('total_rows', 0)

        if processed_rows < total_rows:
            file_stream = StringIO(file_data)
            reader = csv.reader(file_stream)
            next(reader, None)  # Пропускаем заголовок
            for _ in range(processed_rows + 1):
                row = next(reader)

            if len(row) >= 2:
                question, answer = row[0], row[1]
                article = Article(user=request.user, question=question, answer=answer)
                article.save()
                request.session['processed_rows'] = processed_rows + 1
                progress = (processed_rows + 1) / total_rows * 100
                return JsonResponse(
                    {'progress': progress, 'processed_rows': processed_rows + 1, 'total_rows': total_rows})
        else:
            return JsonResponse({'progress': 100, 'processed_rows': total_rows, 'total_rows': total_rows})
    return JsonResponse({'error': 'Invalid request'}, status=400)



@login_required
def search(request):
    query = request.GET.get('query')
    load_dotenv()
    openai_key = os.environ.get("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")
    if query:
        user = request.user
        articles = list(Article.objects.filter(user=user))
        if articles:
            query_vector = get_embeddings(query)
            article_vectors = [eval(article.vector) for article in articles]
            similarities = [cosine_similarity(query_vector, vec) for vec in article_vectors]
            sorted_indices = np.argsort(similarities)[::-1]
            sorted_articles = [articles[i] for i in sorted_indices]
            return render(request, 'themes/search_results.html', {'articles': sorted_articles, 'query': query})
    return render(request, 'themes/search_results.html', {'articles': [], 'query': query})


@login_required
@csrf_exempt
def test_article_relevance(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        test_question = data.get('test_question')
        article_question = data.get('article_question')
        article_answer = data.get('article_answer')

        if test_question and article_question and article_answer:
            combined_text = f"{article_question} {article_answer}"
            articles = list(Article.objects.filter(user=request.user))

            test_vector = get_embeddings(test_question)  # Убедитесь, что указан ваш OpenAI API ключ
            article_vectors = [eval(article.vector) for article in articles]
            article_vectors.append(
                get_embeddings(combined_text))  # Включаем текущую статью в тест
            similarities = [cosine_similarity(test_vector, vec) for vec in article_vectors]

            rank = sorted(similarities, reverse=True).index(similarities[-1]) + 1

            return JsonResponse({'rank': rank})
        return JsonResponse({'error': 'Invalid data'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)