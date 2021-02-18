FROM python:alpine
RUN pip3 install --no-cache-dir bottle dnspython pymongo waitress
WORKDIR /app
COPY . .
CMD python3 app.py