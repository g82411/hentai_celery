FROM python:2.7
ADD requirements.txt /app/requirements.txt
ADD ./crawler/ /app/
WORKDIR /app/
RUN pip install -r requirements.txt