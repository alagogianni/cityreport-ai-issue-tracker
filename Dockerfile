FROM python:3.12-slim
RUN apt-get update && apt-get install -y fonts-freefont-ttf && rm -rf /var/lib/apt/lists/*
# Τα μηνύματα (print) εμφανίζονται αμέσως στα logs του Docker
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Η εφαρμογή τρέχει ως απλός χρήστης, όχι ως root
RUN useradd --create-home appuser && mkdir -p /app/uploads && chown -R appuser:appuser /app
USER appuser
EXPOSE 5000 8501
CMD ["python", "run.py"]
