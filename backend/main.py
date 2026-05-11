from fastapi import FastAPI  # Imports the FastAPI class used to create the backend application.

app = FastAPI()  # Creates the FastAPI application object that Uvicorn needs to run.

@app.get("/")  # Defines a test route for the backend root URL.
def read_root():  # Creates the function that runs when someone visits the root URL.
    return {"message": "Grocery Intelligence Platform API is running"}  # Sends a simple JSON response so we know the API works.