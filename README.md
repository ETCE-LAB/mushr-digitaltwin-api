# MushR DigitalTwin API

## Getting started

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

  ``` bash
  pipenv install
  ```
  
### Usage 
	``` bash
	NEO4J_BOLT_URL="bolt://neo4j:neo4j@localhost:7687/neo4j"
	export $NEO4J_BOLT_URL
	pipenv run python mushr-digitaltwin-api/manage.py runserver
	```
