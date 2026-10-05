FROM python:3.13-alpine@sha256:1a63a53928ce53d2b0baf08092a703f4840ac5dfbd61fd48802dbf48e08c801e
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && adduser -D -u 10001 checkout && mkdir /data && chown checkout /data
COPY server.py .
USER 10001:10001
EXPOSE 8000
CMD ["python", "server.py"]
