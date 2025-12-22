FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 5000
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
CMD ["flask", "run", "--host=0.0.0.0"]