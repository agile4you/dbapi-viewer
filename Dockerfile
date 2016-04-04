FROM python:3.5


WORKDIR /app
COPY dbapi_viewer /app
COPY requirements.txt /app
COPY cmd.sh /
RUN pip install -r requirements.txt

EXPOSE 8081 8081

CMD ["/cmd.sh"]