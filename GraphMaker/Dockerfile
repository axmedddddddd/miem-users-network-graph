FROM python:3.10

WORKDIR /code

COPY ./Pipfile /code/Pipfile
COPY ./Pipfile.lock /code/Pipfile.lock
COPY ./setup.cfg /code/setup.cfg
COPY ./pyproject.toml /code/pyproject.toml

RUN pip install -U pipenv
RUN pipenv install --deploy

COPY ./graphmaker /code/graphmaker

RUN pip install -e .

CMD ["pipenv", "run", "python", "-m", "graphmaker"]
