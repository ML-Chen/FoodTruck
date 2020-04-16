# Food Truck

Phase 4 final project of CS 4400: Intro to Databases, Spring 2020, with Dr. Mark Moss.

Using Flask, Svelte, and MySQL for a food truck management website.

By Michael Chen, Min Htat Kyaw (Reynold), Jingxuan (Julia) Qiu, Duncan Siebert, and Alexander Trotter

## Getting started: server

These steps should be in a terminal in the /server folder (`cd server`).

### Set up virtual environment

This should be a one-time task.

```bash
pip install virtualenv
virtualenv venv
```

### Activate virtual environment

This should be done every time you open a new terminal

Unix (Linux, Mac, or Windows Subsystem on Linux):

```bash
source venv/bin/activate
```

Git Bash on Windows:

```bash
source venv/Scripts/activate
```

Powershell:

```powershell
.\venv\Scripts\activate
```

### Install project dependencies

Next, we need to install the project dependencies, which are listed in `requirements.txt`.

```
(venv) $ pip install -r requirements.txt
```

### Start the server

Start the server:

```
flask run
```

## Tips

To test the backend, you can use the application Postman.