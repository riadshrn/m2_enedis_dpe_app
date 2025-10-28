FROM python:3.11-slim

WORKDIR /app

COPY . /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY models/Compressed /app/models/Compressed
COPY data /app/data


ENV MISTRAL_API_KEY=BwW2Rlm3rbt58NOFOgzzVtIYEhbxw8gp

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
