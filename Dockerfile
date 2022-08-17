FROM python:3.8-slim-buster

# Set labels 
LABEL vendor=SINTEF_Digital \
      SINDIT.is-beta=True\
      SINDIT.version="0.0.1-beta" \
      SINDIT.release-date="2021-05-06"

RUN mkdir /opt/sindit
WORKDIR /opt/sindit
ENV PYTHONPATH /opt/sindit

# Azure
ENV AZURE_URL https://a9adt.api.wcus.digitaltwins.azure.net
ENV AZURE_TENANT_ID 72f988bf-86f1-41af-91ab-2d7cd011db47
ENV AZURE_CLIENT_ID b4add432-56f7-465b-8e9e-e24ccf6d034f
ENV AZURE_CLIENT_SECRET yr38Q~R-hjgyOzPiAbGK.1oTcmPzmPkK4IWjla9R
	  
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y curl && apt-get clean

EXPOSE 8050
EXPOSE 8000

ENTRYPOINT ["/bin/bash", "/opt/sindit/main.sh" ]
