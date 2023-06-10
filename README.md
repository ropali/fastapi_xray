# FastAPI X-ray 🔥
This TUI is designed to streamline the debugging process by providing a comprehensive view of request/response data and tracking all executed SQL queries. This tool empowers developers to effectively diagnose and resolve issues related to database interactions.

Key Features:

- Request/Response Data Debugging: Gain deep insights into the data exchanged between client applications and the server. Easily identify and analyze the content and structure of both incoming requests and outgoing responses.

- SQL Query Tracking: Track every SQL query executed during the application runtime. Monitor query performance, detect bottlenecks, and optimize database interactions for enhanced efficiency.

## Screenshots
![image](https://github.com/ropali/fastapi_xray/assets/31515245/504a8da8-f366-4f1c-ba56-cd798cb70a91)

![image](https://github.com/ropali/fastapi_xray/assets/31515245/cc1fb459-f4b3-45ff-ae66-1c5a48316f6c)

## Installation
Install this package from pypi using this command.
```
pip install fastapi-xray
```

## Usage
It is very easy to use. Call the `start_xray` function to start intercepting all the request and response.

```
from fastapi import FastAPI
from sqlalchemy import create_engine

from fastapi_xray import start_xray

# create SQLAlchemy engine
engine = create_engine("sqlite:///app.db")

app = FastAPI()

# Pass the instance of app and sql engine to the function.
# Passing the sql engine instance is optional
# if you are not using any database.
# NOTE: Not recommended to use it in the production.

if os.environ["DEBUG"]:
    start_xray(app, engine)
```

Start the CLI to see the incoming requests in the terminal. Use this command to start the terminal interface.
```
fastapi_xray # starts the xray server at 8989 port
```
Use the `--help` command to see all the configurable options.
