FROM python:3

WORKDIR /usr/src/app/scraper

RUN pip install selenium requests

COPY main.py ./

CMD ["python", "./main.py"]