FROM python:3.8-slim

COPY requirements.txt ./app/

WORKDIR /app

RUN python -m pip install --upgrade pip

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "corpquiz.wsgi:application", "--bind", "0:8000" ]