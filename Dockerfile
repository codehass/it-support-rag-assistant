FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./app /code/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
