# Corporate quiz backend

![CorpQuiz backend](https://github.com/Corporate-Quiz/backend/actions/workflows/workflow.yml/badge.svg)


**Описание**  
Backend для приложения «Корпоративный Quiz»: сервиса, позволяющего проводить квизы, тесты и обучение для сотрудников.

**Технологии:**  
- [Python](https://www.python.org/doc/) 
- [Django](https://docs.djangoproject.com/en/4.2/releases/4.2.2/)
- [Django REST framework](https://www.django-rest-framework.org/)


---
## Документация  

### **Запуск проекта:**

- **Клонируем репозиторий:**  
    ```bash
    git clone https://github.com/Corporate-Quiz/backend.git
    ```  
- **Переходим в коталог с поектом:**
    ```bash
    cd backend/
    ```
- **Применяем миграции:**  
    ```bash
    python manage.py migrate
    ```
- **Собираем статику:**  
    ```bash
    python manage.py collectstatic --no-input 
    ```
- **Создаем суперпользователя:**  
    ```bash
    python manage.py createsuperuser
    ```
- **Запускаем проект:**  
    ```bash
    python manage.py runserver
    ```

**API доступно по адресу:**  
```bash
http://127.0.0.1:8000/api/v1/ 
```

**Админка:**  
```bash
http://127.0.0.1:8000/admin/ 
```


---
## Документация API:  

Полный список возможных запросов к API можно посмотреть по этому адресу:
```bash
http://127.0.0.1:8000/docs/swagger/ 
```

---

