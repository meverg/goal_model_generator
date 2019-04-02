FROM python:3.7
RUN pip install pipenv
RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_md-2.1.0/en_core_web_md-2.1.0.tar.gz
COPY ./optimathsat_linux /app/optimathsat
COPY ./Pipfile* /app/

WORKDIR /app

RUN pipenv install --system --deploy --ignore-pipfile

COPY ./.env_prod /app/.env
COPY . /app

EXPOSE 5000

CMD flask run --host=0.0.0.0