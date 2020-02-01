# gcp-inventory
Inventory of GCP resources

## Pre-requisite

https://cloud.google.com/python/setup?hl=fr

```pip install google-cloud-asset``` (en bêta)
```pip install google-api-python-client```

```gcloud components install app-engine-python```

See documentatoion on https://pypi.org/project/google-cloud-asset/

Else you'll have to install all needed packages ```pip install google-cloud-storage``` ??

### Homepage and API docs

https://github.com/googleapis/google-cloud-python

https://googleapis.dev/python/cloudasset/latest/index.html

## Authentication
https://googleapis.dev/python/google-api-core/latest/auth.html

Google says that using a service account is a better solution than enduser credentials (Google SDK user), because of possible API quota limitation.

Tip: Don't use quotes in ```set GOOGLE_APPLICATION_CREDENTIALS=./file.json```! 

In Visual Studio Code, use ```launch.json``` to set the authentication like that:
```{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python : Fichier actuel",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "env": {
                "GOOGLE_APPLICATION_CREDENTIALS":"./cred.json"
            }
        }
    ]
}```

### Setting up a service account




