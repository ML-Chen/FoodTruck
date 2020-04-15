# Food Truck Server

Flask server for our food truck app. Python ≥3.7 is recommended.

## Getting Started

For these steps, make sure that your terminal is in the /server folder.

### Set up virtual environment

This should be a one-time task.

```bash
pip install virtualenv
virtualenv venv
```

### Activate virtual environment

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

Create a new file named `.env` by duplicating `.env.example`. Update the new file with the GitHub credentials. It should look similar to this:

```
# .env file
DATABASE_URL="[INSERT_DATABASE_URL]"
GITHUB_CLIENT_ID="[INSERT_CLIENT_ID]" # placeholder from template
GITHUB_CLIENT_SECRET="[INSERT_CLIENT_SECRET]" # placeholder from template
```

Now we're ready to start our server which is as simple as:

```
(venv) $ flask run
```

Open http://localhost:5000 to view it in your browser.

The app will automatically reload if you make changes to the code.
You will see the build errors and warnings in the console.

## Tips

If you need to install a new package (say it's named "package") and add it to `requirements.txt`, you can run something like the following in Bash or Git Bash: `pip install package && pip freeze > requirements.txt`

## What's Included?

- [Flask](http://flask.pocoo.org/) - A microframework for Python web applications
- [Flask Blueprints](http://flask.pocoo.org/docs/1.0/blueprints/) - A Flask extension for making modular applications
- [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.3/) - A Flask extension that adds ORM support for your data models.
- [Werkzeug](http://werkzeug.pocoo.org/) - A Flask framework that implements WSGI for handling requests.
- [Bootstrap 4](https://getbootstrap.com/) - An open source design system for HTML, CSS, and JS.
- [Jinja2](http://jinja.pocoo.org/docs/2.10/) - A templating language for Python, used by Flask.
