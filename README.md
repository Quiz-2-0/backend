# Corporate quiz backend

![CorpQuiz backend](https://github.com/Corporate-Quiz/backend/actions/workflows/workflow.yml/badge.svg)
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

### Установка pre-commit hooks

Для того, чтобы при каждом коммите выполнялись pre-commit проверки, необходимо:
- Установить pre-commit
- Установить pre-commit hooks

#### Установка pre-commit
Модуль pre-commit уже добавлен в requirements и должен установиться автоматически с виртуальным окружением.

Проверить установлен ли pre-commit можно командой (при активированном виртуальном окружении):
```sh
pre-commit --version
>> pre-commit 3.4.0
```

Если этого не произошло, то необходимо установить pre-commit:
```sh
pip install pre-commit
```

#### Установка hooks
Установка хуков:
```sh
pre-commit install --all
```
Установка хука для commitizen
```sh
pre-commit install --hook-type commit-msg
```
В дальнейшем, при выполнении команды git commit будут выполняться проверки, перечисленные в файле .pre-commit-config.yaml.

Если не видно, какая именно ошибка мешает выполнить commit, можно запустить хуки вручную командой:
```sh
pre-commit run --all-files
```

### Работа с commitizen
Установите commitizen
```sh
pip install commitizen
```
Чтобы сгенерировать установленный git-commit, запустите в вашем терминале
```sh
cz commit
```
или сочетание клавиш
```sh
cz c
```
---
## Документация API:

Полный список возможных запросов к API можно посмотреть по этому адресу:
```bash
http://127.0.0.1:8000/docs/swagger/
```

---
