FROM python:3.5


WORKDIR /app
COPY requirements.txt /app
COPY cmd.sh /
RUN pip install -r requirements.txt
WORKDIR /dbapi_viewer
EXPOSE 8081 8081

CMD ["/cmd.sh"]