FROM python:3.7-slim

ARG DEVELOPMENT

# Install pip dependencies
WORKDIR /kb/module
COPY ./requirements.txt /kb/module
COPY ./dev-requirements.txt /kb/module

# Install deps and run the app
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential && \
    pip install --upgrade --no-cache-dir pip -r requirements.txt && \
    if [ "$DEVELOPMENT" ]; then pip install --no-cache-dir -r dev-requirements.txt; fi && \
    apt-get purge -y --auto-remove gcc build-essential

COPY . /kb/module
RUN chmod -R a+rw /kb/module

ENTRYPOINT ["sh", "/kb/module/src/scripts/entrypoint.sh"]
