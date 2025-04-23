FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/db

EXPOSE 5000 8501

RUN echo '#!/bin/bash\n\
python app.py &\n\
streamlit run streamlit_app.py\n'\
> /app/start.sh

RUN chmod +x /app/start.sh

# Command to run both services
CMD ["/app/start.sh"]
