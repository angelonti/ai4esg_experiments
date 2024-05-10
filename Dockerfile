FROM python:3.11

WORKDIR /app

RUN apt clean && \
    apt update && \
    apt install -y --no-install-recommends --fix-missing python3-opencv

COPY backend /app/
COPY entrypoint.sh /app/entrypoint.sh
COPY demo.env /app/demo.env
COPY frontend/app.py /app/app.py
COPY frontend/data.py /app/data.py
COPY frontend/.streamlit /app/.streamlit
RUN rm -rf /app/AutoGPTQ

RUN pip3 install --no-cache-dir --user -r requirements.txt




EXPOSE 8080

RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["bash", "-c", "/app/entrypoint.sh"]
