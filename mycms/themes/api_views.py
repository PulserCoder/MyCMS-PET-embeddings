import os

import numpy as np
from dotenv import load_dotenv
from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Article, UserProfile
from .serializers import GetMostRelevantAnswersSerializer
from openai import OpenAI
from httpx import Client

load_dotenv()
api_key_openai = os.environ.get("OPENAI_API_KEY")

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def get_embeddings(text):
    proxy_url = "http://xjBREP:RQszmz@45.155.200.222:8000"
    http_client = Client(proxies={"http://": proxy_url, "https://": proxy_url})
    openai = OpenAI(api_key=api_key_openai, http_client=http_client)
    response = openai.embeddings.create(model="text-embedding-ada-002", input=[text])
    return response.data[0].embedding


class GetMostRelevantAnswersView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        api_key = request.headers.get('API-Key')
        if not api_key:
            return Response({'error': 'API Key is required'}, status=status.HTTP_403_FORBIDDEN)

        try:
            user_profile = UserProfile.objects.get(api_key=api_key)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Invalid API Key'}, status=status.HTTP_403_FORBIDDEN)

        serializer = GetMostRelevantAnswersSerializer(data=request.data)
        if serializer.is_valid():
            user_input = serializer.validated_data['user_input']

            user = user_profile.user
            articles = list(Article.objects.filter(user=user))  # Преобразуем в список
            if not articles:
                return Response({'error': 'No articles found for this user'}, status=status.HTTP_404_NOT_FOUND)
            print(articles[0].combined)
            print(user_input)
            vectors = [article.vector for article in articles]
            user_vector = get_embeddings(user_input)
            similarities = [cosine_similarity(user_vector, eval(vec)) for vec in vectors]

            top_indices = np.argsort(similarities)[-5:][::-1]
            relevant_answers = [articles[i].answer for i in top_indices]

            proxy_url = "http://xjBREP:RQszmz@45.155.200.222:8000"
            http_client = Client(proxies={"http://": proxy_url, "https://": proxy_url})
            openai = OpenAI(api_key=api_key_openai, http_client=http_client)
            result_text = ''

            for answer in relevant_answers:
                prompt = f'Tell me "YES" if there is an answer to this question "{user_input}" in this text - "{answer}". Otherwise, say NO.'
                model = 'gpt-3.5-turbo-0301'
                messages = [{'content': prompt, 'role': 'system'}]
                result = openai.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.1
                )
                ans = result.choices[0].message.content
                print(ans)
                if "YES" in ans.upper():
                    result_text += answer + '\n'

            return Response({'result': result_text})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






