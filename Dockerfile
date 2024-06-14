FROM python:3.11

WORKDIR /app

COPY sshd_config /etc/ssh/

COPY backend /app/
COPY entrypoint.sh /app/entrypoint.sh
COPY demo.env /app/demo.env
COPY frontend/app.py /app/app.py
COPY frontend/pages /app/pages
COPY frontend/.streamlit /app/.streamlit

RUN apt clean && \
    apt update && \
    apt install -y --no-install-recommends --fix-missing python3-opencv

RUN apt update \
    && apt install -y --no-install-recommends dialog \
    && apt install -y --no-install-recommends openssh-server \
    && echo "root:Docker!" | chpasswd

RUN chmod u+x /app/entrypoint.sh
RUN rm -rf /app/AutoGPTQ

RUN pip3 install --no-cache-dir --user -r requirements.txt

EXPOSE 8000 2222 8080

ENTRYPOINT ["bash", "-c", "/app/entrypoint.sh"]
