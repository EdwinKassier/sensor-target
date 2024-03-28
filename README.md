## Introduction

This is a flask based repository aimed at ingesting and providing an api for a static dataset of sensor IOT data

## Requirements
* Python3
* Docker Desktop

## Getting started

1. Build the docker image by running ```docker compose build``` , this will create and store your image with all relevant pip libraries pre-installed in your Docker Desktop enviornment 
2. To run the docker image you can use ```docker compose up```, thi will start the image and the flask process within it, you can find the targetable endpoints in the provided ```openapi-3.0.yaml``` file on your localhost (http://127.0.0.1:8080/)


## Understanding the API
The structure of the api (including parameters required, expected responses etc.) has been set out in the openapi.yaml file, this adheres to the OpenAPI 3.0 structure, and is consistent with tools like Swagger.

For further learnings you can look at the Flask_Tutorial.md file

## Test the application
All the tests for this api are functional tests using pytest

1. To run the test suite, open the docker desktop program and open the ```exec``` tab, when in this tab use the following command:  ```pytest``` to run all available tests


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

