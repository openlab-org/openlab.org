# WIP

Project under development!

# openlab.org

Discover and collaborate on open hardware

![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg)

# Getting started

## Without Docker

It's much simpler to run a dev environment without Docker, just using
`virtualenv` and using `sqlite3` as the backend. This *will not* resemble
production environments. However, it is very light and often easier to setup
and is good enough for most development.

1. Install Python 3, including `pip` and `venv`, and system packages for sqlite3
    * On Debian-based distros:
        * `sudo apt-get install sqlite3 python3 python3-env python3-pip`
    * On macOS, use something like `brew`
2. Create a virtualenv. For example:
    * `mkdir -p ~/.venvs/`
    * `python3 -m venv ~/.venvs/openlab`
3. Activate virtualenv:
    * `source ~/.venvs/openlab/bin/activate`
    * You will need to do this any time you want to work
4. Install dependencies:
    * `pip install -r requirements/local.txt`
5. Run migrations to setup sqlite database file:
    * `python manage.py migrate`
6. Start the server:
    * `python manage.py runserver`

## With Docker

TODO: Unfinished

1. Install and set up system packages for `docker` and `docker-compose`:
    * On Debian-based distros:
        * `sudo apt-get install docker docker-compose`
    * [On macOS, follow this guide](https://docs.docker.com/docker-for-mac/)


# Useful tools
* `python manage.py testreset --traceback` -- Populates the DB with a bunch of
  test data

* `./utility/dev/delete_db_and_remake_migrations.sh` -- Running this will
  delete the Sqlite database, delete all migration code for Open Lab apps, then
  rebuild all migration code. Until we have a stable prod environment that we
  don't want to trash, this keeps our migrations tidy as we iterate over
  schema.




