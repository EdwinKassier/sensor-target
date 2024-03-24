## Introduction

Project Delos answers the question: If I had bought a crypto currency when it first appeared on the public exchange, would I have enough money to buy a lambo if I sold my coins in the last month?

This is the Flask backend version for the system

## Requirements
* Python3
* Pipenv

## Getting started

1. Source the virtual environment ```[pipenv shell]```
2. Install the dependencies ```[pipenv install]```


## Run the application
You will need two terminals pointed to the frontend and backend directories to start the servers for this application.

1. To run the backend, make sure you have started the pipenv shell using ```[pipenv shell]```
2. Run this command to start the backend server: ```[python run.py]``` (You have to run this command while you are sourced into the virtual environment)

## Understanding the API
The structure of the api (including parameters required, expected responses etc.) has been set out in the openapi.yaml file, this adheres to the OpenAPI 3.0 structure, and is consistent with tools like Swagger.

For further learnings you can look at the Flask_Tutorial.md file

## Test the application
All the tests for this api are functional tests using pytest

1. To run the test suite, use the following command:  ```[python -m pytest]```


## The Build Pipeline
The CI/CD pipeline for the api is broken up into three stages

1. Linting and Quality Assurance using pylint to ensure code quality is above a certain threshold as well as catching any critical quality issues
2. Testing, here we run the unit tests set out in our pytest files
3. Building and deployment, here the container is built and pushed to container registry on GCP and the code is packaged to be run on that container, with traffic being cut over to the new version once the build is complete

This pipeline can be found in the github workflows folder in the push.yml file

![Alt text](BuildPipeline.png?raw=true "Title")

## Bringing the code to production
This code encompasses the backend for a larger system, in the diagram below I have set out the architecture that could be used to create an enterprise ready system that meets all the needs of a high availability and low latency web app.

I have used GCP for the example, but have chosen the components to be as simplistic as possible, to most easily be portable to other cloud providers using some kind of resource management language like terraform

This architecture would use github actions as its CI/CD pipeline using the included push.yml file, but could be updated to use something else within the CI/CD ecosystem like Jenkins

![Alt text](Architecture.png?raw=true "Title")

