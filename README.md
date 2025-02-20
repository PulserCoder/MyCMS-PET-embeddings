# MyCMS

## Описание проекта

**MyCMS** — это pet-проект, разработанный для управления базой знаний компании, используемой умным помощником (ИИ-ассистентом). Система позволяет проверять релевантность статей, анализировать, закрывают ли статьи наиболее часто задаваемые вопросы, а также редактировать и удалять записи в базе знаний.

## Функциональность

- Проверка релевантности статей в базе знаний.
- Анализ покрытия базы знаний по часто задаваемым вопросам.
- Изменение, удаление и обновление статей.
- Удобный интерфейс для управления базой знаний.

## Технологии

- **Backend**: Django
- **База данных**: SQLite (временно)
- **Дополнительные библиотеки**:
  - djangorestframework
  - openai (используется технология embeddings OpenAI)
  - numpy
  - pydantic
  - python-dotenv

## Зависимости

```sh
annotated-types==0.6.0
anyio==4.3.0
asgiref==3.8.1
certifi==2024.2.2
distro==1.9.0
Django==5.0.6
djangorestframework==3.15.1
exceptiongroup==1.2.1
h11==0.14.0
httpcore==1.0.5
httpx==0.27.0
idna==3.7
numpy==1.26.4
openai==1.30.1
pydantic==2.7.1
pydantic_core==2.18.2
python-dotenv==1.0.1
sniffio==1.3.1
sqlparse==0.5.0
tqdm==4.66.4
typing_extensions==4.11.0
```

## Запуск проекта

### Установка зависимостей

```sh
pip install -r requirements.txt
```

### Запуск миграций

```sh
python manage.py migrate
```

### Запуск сервера

```sh
python manage.py runserver
```

## Развертывание

Развертывание пока не выполнено.

## Контакты

Если у вас есть вопросы или предложения, вы можете связаться со мной через **@pkuzmin_d**.

