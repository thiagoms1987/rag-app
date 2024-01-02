# Function: Python "rag"

## Introduction

This repository contains a project that create serverless function 'Talk to PDF' written in Python. You are able to ask questions about the content of a PDF file. You can deploy it on DigitalOcean's App Platform as a Serverless Function component.
Documentation is available at https://docs.digitalocean.com/products/functions.

### Requirements

* You need a DigitalOcean account. If you don't already have one, you can sign up at [https://cloud.digitalocean.com/registrations/new](https://cloud.digitalocean.com/registrations/new).
* You need a OpenAI account. If you don't already have one, you can sign up at [https://chat.openai.com/auth/login]
* You need a Pinecone account. If you don't already have one, you can sign up at [https://www.pinecone.io/].
* You need to add your `OPENAI_API_KEY` to the `.env` file to connect to the OpenAI API.
* You need to add your `PINECONE_API_KEY` and `PINECONE_API_ENV` to the `.env` file to connect to the Pinecone.
* To deploy from the command line, you will need the [DigitalOcean `doctl` CLI](https://github.com/digitalocean/doctl/releases).


## Deploying the Function

```bash
# clone this repo
git clone git@github.com:thiagoms1987/rag-app.git
```

```
# deploy the project, using a remote build so that compiled executable matched runtime environment
> doctl serverless deploy rag-app --remote-build
Deploying 'rag-app'
  to namespace 'fn-...'
  on host 'https://faas-...'
Submitted action 'rag' for remote building and deployment in runtime python:default (id: ...)

Deployed functions ('doctl sls fn get <funcName> --url' for URL):
  - rag/rag
```

## Using the Function

```bash
doctl serverless functions invoke rag/rag -p userprompt:message.
```
```json
{
  "response": "message"
}
```

### To send a query using curl:
```
curl -X PUT -H 'Content-Type: application/json' {your-DO-app-url} -d '{"userprompt":"message"}' 
```

### Learn More

You can learn more about Functions and App Platform integration in [the official App Platform Documentation](https://www.digitalocean.com/docs/app-platform/).