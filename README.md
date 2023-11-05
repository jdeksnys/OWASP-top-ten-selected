# BankApp

## About
Simple Django web app, showcasing 5 security flaws from the OWASP Top Ten 2021 list, and their fixes.

## Setup
- To create + seed local database, in terminal run `manage.py migrate`  
- To setup application in unsecure mode (with security flaws), set `IS_SECURE=False` in `settings.py`. Default value is `True`.  
- To start local server, run `manage.py runserver`.


## Testing
App contains two customers for testing:
1)  Social security number: 101  
    Password: squarepants

2)  Social security number: 102  
    Password: redqueen
