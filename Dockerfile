FROM python:3.7-slim

ARG DEVELOPMENT

# Install pip dependencies
COPY . /kb/module
RUN chmod -R a+rw /kb/module

# Install deps and run the app
WORKDIR /kb/module
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential && \
    pip install --upgrade --no-cache-dir pip -r requirements.txt && \
    if [ "$DEVELOPMENT" ]; then pip install --no-cache-dir -r dev-requirements.txt; fi && \
    apt-get purge -y --auto-remove gcc build-essential
ENTRYPOINT ["sh", "/kb/module/src/scripts/entrypoint.sh"]
