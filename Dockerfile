FROM python:3.9

COPY ./requirements.txt /webapp/requirements.txt
COPY ./index.py /webapp
COPY ./app.py /webapp
COPY ./helperfns.py /webapp

WORKDIR /webapp

ENV PIP_NO_CACHE_DIR=1

RUN pip install -r requirements.txt

CMD [ "python","index.py" ]
EXPOSE 5000