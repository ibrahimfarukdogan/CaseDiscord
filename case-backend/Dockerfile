FROM python:3.10-bullseye

WORKDIR /

RUN git config --global url.ssh://git@github.com/.insteadOf https://github.com/
RUN mkdir -p -m 0600 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    gcc \
    gettext \
    libpq-dev \
    cron \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY poetry.lock /
COPY pyproject.toml /
RUN --mount=type=ssh poetry install
COPY ./ ./
# COPY ./entrypoint.sh ./

RUN sed -i 's/\r$//g' /entrypoint.sh
RUN chmod +x /entrypoint.sh
# uvicorn: asgi web server implementation for python
#collectstatic: css sayfalarini yukler, admin icin gerekli
CMD python manage.py collectstatic --noinput && python -m uvicorn app.asgi:application --host 0.0.0.0 

EXPOSE 8000
