# Food Truck

Team 39 Phase 4 final project of CS 4400: Intro to Databases, Spring 2020, with Dr. Mark Moss.

Using Flask, Svelte, and MySQL for a food truck management website.

Contributors (and their primary Georgia Tech username):
- Michael Chen (mchen419)
- Min Htat Kyaw (mkyaw6)
- Alexander Trotter (atrotter6)
- Duncan Siebert (dsiebert3) – opted to take the final exam

## Getting started: server

Make sure you have [Python ≥3.7](https://www.python.org/downloads/) installed.

These steps should be in a terminal in the /server folder (`cd server`).

You can skip the "Set up virtual environment" and "Activate virtual environment" steps if you're okay with installing the pip packages globally on your computer. With bigger projects it would be a good idea to use a virtual environment, however.

### Set up virtual environment

This should be a one-time task.

```bash
pip install virtualenv
virtualenv venv
```

### Activate virtual environment

This should be done every time you open a new terminal

- Unix (Linux, Mac, or Windows Subsystem on Linux): `source venv/bin/activate`
- Git Bash on Windows: `source venv/Scripts/activate`
- Powershell: `.\venv\Scripts\activate`

### Install project dependencies

Next, we need to install the project dependencies, which are listed in `requirements.txt`.

```
pip install -r requirements.txt
```

### Set your database password

Change `.env` to your match your database address, password, etc.

### Start the server

Start the server on port 4000:

```
flask run -p 4000
```

It may be helpful to first enable debug mode beforehand:

- Git Bash, Unix (Linux, Mac, or Windows Subsystem on Linux): `export FLASK_ENV=development`
- Windows Command Prompt (CMD): `set FLASK_ENV="development"`
- PowerShell: `$env:FLASK_ENV="development"`

### Tips

To test the backend, you can use the application [Postman](https://www.postman.com/).

## Getting started: client

Install [Node.js](https://nodejs.org/en/) and [Git](https://git-scm.com/downloads).

Now, in a separate terminal in the /client folder (`cd client`), run:

```
npm install
npm run dev
```

The website will be available at http://localhost:5000.

If that doesn't work, try:

```
npm run build
npm run serve
```
