# BankApp

## About
Simple Django web app, showcasing 5 security flaws from the OWASP Top Ten 2021 list, and their fixes (see comments in code, `IS_SECURE` variable).  
The app imitates a simple bank with customers, login page and money transfer functionality.

## Setup (via terminal)
1. Clone repository. Run interminal:
```
git clone https://github.com/jdeksnys/OWASP-top-ten-selected
```   
3. Create + seed local database
```
manage.py migrate
```   
4. To setup application in unsecure mode (run with security flaws), set `IS_SECURE=False` in `settings.py`. Default value is `True`.   
5. Start local server, run in terminal:
```
manage.py runserver
```


## Testing
App contains two customers for testing:
1)  Social security number: 101  
    Password: squarepants

2)  Social security number: 102  
    Password: redqueen
