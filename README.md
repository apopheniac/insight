# Insight Analytics

A web app that allows a user to upload data and make sense of it, across an organization.

## Getting Started

These instructions will get the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project to Google Cloud Platform.

### Prerequisites

_Local development_

- Docker
- Docker Compose
- A Google account for access to the Sheets API
- [Optional] MyPy for static type checking

_Deployment_

- Google Cloud SDK

### Installing

Follow the instructions in the [Sheets API Quickstart for Python](https://developers.google.com/sheets/api/quickstart/python) to generate and save credentials for access to the Sheets API.

Make a copy of the `.env.example` file and rename it to `.env`. Update the `GOOGLE_APPLICATION_CREDENTIALS` key with the name of your Google Sheets credential file, and provide a Postgres username and password.

To build and run the app, run 

```
docker-compose up
```
at the project root. Check the output of the docker-compose command for the local URL at which you will find the running app, e.g. http://0.0.0.0:5000/ 


## Running tests

You can execute the test suite by running `pytest` in the project root. 

## Deployment

Assuming you have access to the Google Cloud Platform project where the app is hosted, you can run 

```
gcloud builds submit
```

to deploy it to Google Cloud Run.

## Roadmap

- Poll Google Sheets and sync data to Postgres. (At the moment, the app just reads data from Sheets at startup and retains it in memory.)
- Optimise UI for mobile devices. 

## Built With

* [Dash](https://dash.plotly.com/) - Python framework for data visualisation
* [Flask](https://palletsprojects.com/p/flask/) - Python web microframework
