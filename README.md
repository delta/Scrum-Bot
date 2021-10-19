# Scrum Bot

A discord bot used to track messages sent on discord during a scrum, and a frontend to view it.

## Prerequisites

- Python >3.6

## Setup Instructions

### Backend

- Clone the repo, and create a new python virtual environment, with the command

  ```bash
   python3 -m venv venv
  ```

- Activate the virtual environment by running the command

  ```bash
    source venv/bin/activate
  ```

  > You will see (venv) in your terminal after you run this command

- Install the all the dependencies from requirements.txt by running the comma>

  ```bash
    pip install -r backend/requirements.txt
  ```

- Create .env file from backend/.env.example

  ```bash
    cp backend/.env backend/.env.example
  ```

- Generate secure secrets for jwt-secret and bot-tokens

  ```bash
    openssl rand -hex 32
  ```

- If you install a new package, add the package to requirements.txt by running

  ```bash
    pip freeze > requirements.txt
  ```

- To exit the virtual environment by entering the command, `deactivate`

## Running Instructions

### Backend

- To start the server run

  ```bash
  python3 backend/main.py
  ```

## Contributors

- Ajitha Prasad [kelpikz](https://github.com/kelpikz)
