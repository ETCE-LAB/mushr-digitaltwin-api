# MushR DigitalTwin API

The MushR DigitalTwin API is a simple digital twin impementation for
Gourmet Mushroom production. Please check
<https://github.com/ETCE-LAB/MushR.git> for more information about the
MushR project.

The API is modelled using
[Neomodel](https://github.com/neo4j-contrib/neomodel) (an Object Graph
Mapper (OGM) for the Neo4j Graph Database), that is exposed as a REST
API using the [Django REST
Framework](https://www.django-rest-framework.org/).

## Features
- OpenAPIv3 and SwaggerUI support via [drf-yasg](drf-yasg.readthedocs.io/).

### Security Features

-  Oauth2.0 support via
  [django-oauth-toolkit](https://github.com/jazzband/django-oauth-toolkit)
  for Authentication and Authorization.


## Getting started

### External Runtime Dependencies

1. This API does not store the digital twin api, and depends on an
   existing neo4j (>=4.0) database to store it's data. For development
   purposes this server can be run on localhost.
2. Please ensure that the neo4j server exposes at least the bolt
   interface.


### Installing

- Clone the Repository
	```
  git clone git@gitlab.tu-clausthal.de:as83/mushr-digitaltwin-api.git
  
  cd mushr-digitaltwin-api
  ```
  
- Install Pipenv

  ```
  pip install --upgrade pipenv
  ```

- Install project dependencies

  ```
  pipenv install
  ```
  
### Usage 


#### Development Server

1. Set `DEBUG = True` in [settings.py](mushr_digitaltwin_api/mushr_digitaltwin_api/mushr_digitaltwin_api/settings.py), otherwise static files will not be hosted by the development server

2. Set required environment variables and run server:

	```
	export SECRET_KEY="<Insert Securely generated secret-key here>"
	export ALLOWED_HOSTS="localhost 127.0.0.1 www.example.com <insert-your-domain-name-here>"
	export NEO4J_BOLT_URL="bolt://<neo4j-username>:<neo4j-password>@<neo4j-server address>:<BOLT PORT (Usually 7687)>/<databse-name>"
	pipenv run python mushr-digitaltwin-api/manage.py runserver

	```
	
### Production Server

   1. Ensure that `DEBUG=False` in
      [settings.py](mushr_digitaltwin_api/mushr_digitaltwin_api/mushr_digitaltwin_api/settings.py)
   
   2. Also go through the [django deployment
      checklist](https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/).

   3. Fetch the static files used by the project:
   
   ```
   pipenv run python3 mushr_digitaltwin_api/manage.py collectstatic
   ```
   
   4. Please refer to the official django documentation for [deploying
      the static files in
      production](https://docs.djangoproject.com/en/dev/howto/static-files/deployment/).
   
   5. Deploy the Django project using your favourite [web
      server](https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/)
      (both `uvicorn` and `gunicorn` webservers have been tested and
      are already added as dependencies in the Pipfile)
