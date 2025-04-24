FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/db

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_DEBUG=0
ENV PYTHONUNBUFFERED=1

# Set Streamlit server address to listen on all interfaces
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

EXPOSE 5000 8501

# Run both services with proper host configuration
CMD bash -c "flask run --host=0.0.0.0 --port=5000 & streamlit run --server.address=0.0.0.0 --server.port=8501 streamlit_app.py"
