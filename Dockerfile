FROM python:3.10
RUN apt-get update -qy
COPY . .
WORKDIR .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "MainServer.app:app", "--host", "0.0.0.0"]

