import secrets

from django.contrib.auth.models import User
from django.db import models
from httpx import Client
from openai import OpenAI


class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    question = models.TextField()
    answer = models.TextField()
    combined = models.TextField()
    vector = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Связь с пользователем

    def __str__(self):
        return self.question[:50]  # Отображение первых 50 символов вопроса

    def save(self, *args, **kwargs):
        self.combined = f"{self.question} {self.answer}"
        self.vector = self.get_embeddings(self.combined)
        super().save(*args, **kwargs)

    def get_embeddings(self, text):
        api_key = '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'  # Убедитесь, что у вас установлен API ключ
        proxy_url = "http://xjBREP:RQszmz@45.155.200.222:8000"
        http_client = Client(proxies={"http://": proxy_url, "https://": proxy_url})
        openai = OpenAI(api_key=api_key, http_client=http_client)
        response = openai.embeddings.create(model="text-embedding-ada-002", input=[text])
        return response.data[0].embedding


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=50, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = self.generate_api_key()
        super().save(*args, **kwargs)

    def generate_api_key(self):
        return secrets.token_urlsafe(32)


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
