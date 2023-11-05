# OWASP-top-ten-selected

## About
Simple Django web app, showcasing 5 security flaws from the OWASP Top Ten 2021 list, and their fixes.

## Setup
To create + seed local database, in terminal run `manage.py migrate`  
To setup application in unsecure mode (with security flaws), set `IS_SECURE=False` in `Settings.py`. Default value is `True`.  
To start local server, run `manage.py runserver`.
