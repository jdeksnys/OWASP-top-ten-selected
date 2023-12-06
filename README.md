# BankApp

## About
Simple Django web app, showcasing 5 security flaws from the OWASP Top Ten 2021 list, and their fixes (see comments in code, `IS_SECURE` variable).  
The app imitates a simple bank with customers, login page and money transfer functionality.

## Setup
1. Clone repository:
```
git clone https://github.com/jdeksnys/OWASP-top-ten-selected
```   
2. Navigate to root:
```
cd OWASP-top-ten-selected
```   
3. Create + seed local database:
```
manage.py migrate
```
4. To setup application in unsecure mode (run with security flaws), set `IS_SECURE=False` in `settings.py`. Default value is `False`.   
5. Start local server:
```
manage.py runserver
```


## Testing
App contains two customers for testing:
1)  Social security number: 101  
    Password: squarepants

2)  Social security number: 102  
    Password: redqueen

## Essay
OWASP TOP TEN: 2021
FRAMEWORK: Django



### FLAW 1: Identification and Authentication Failures

SPECIFIC ISSUES:
	CWE-1216 Lockout Mechanism Errors [1]: allowing unlimited sign in attempts and lack of exponentially increasing sign-in lock time after number of tries exceeded, Session fixation: not logging out on browser close.

CODE SOURCES:
	L36-L45 views.py
https://github.com/jdeksnys/OWASP-top-ten-selected/blob/5d531f1873cde9882f6faf9f8a32c8683e569427/BankApp/views.py#L36-L45
	L119 settigns.py
https://github.com/jdeksnys/OWASP-top-ten-selected/blob/5d531f1873cde9882f6faf9f8a32c8683e569427/BankApp/settings.py#L119

DESCRIPTION:
	First, we skip some trivial security design flaws such as hashing passwords and generic undisclosed failed login error messages. Unlimited sign in attempts refers to being able use password brute force attacks unlimitedly, thus in theory posing no restriction to guessing a user's password. Important: we only assume this threat for a specific user only - we skip the problem of unlimited sign in attempts for different usernames as this would require IP checking and blocking techniques which are outside the scope of this course.
	Keeping session active on window close poses risk of the SessionId cookie being stolen or simply physically leaving access to the user's account on the same machine for others (ex: public computer in library).

HOW TO FIX:
	Introduce a fixed number (three) of possible attempts, after which the login becomes unavailable for some time (30 seconds). If the users logs-in with the correct password, they are forwarded to the main page. If the user fails again (4th time in row), the login form is blocked for twice the time period (60 seconds). If fails to login once again, the login form is blocked for double the time once again (120 seconds) and so on... See code sources for implementation.
	In Django settings.py, the set SESSION_EXPIRE_AT_BROWSER_CLOSE=True. This enabled browser length sessions, meaning cookies will expire not when SESSION_COOKIE_AGE is reached, but when the browser is closed. Important: session expires when browser, not tab is closed. This also means fully shutting down the browser (ex: "quit" vs "close" on Safari).




### FLAW 2: A01:2021 – Broken Access Control

SPECIFIC ISSUE:
	CWE-285: Improper Authorization [8]

CODE SOURCE:
	L93-L101 views.py
https://github.com/jdeksnys/OWASP-top-ten-selected/blob/5d531f1873cde9882f6faf9f8a32c8683e569427/BankApp/views.py#L93-L101
	
DESCRIPTION:
	Users lack permission to perform specific actions (requests). In the BankApp example, permission to transfer funds is required. However, if access controls are not applied or applied incorrectly (too many privileges), users are able to access data or perform actions they should not be able to. This could result in information exposures, denial or service, arbitrary code execution [8]. In these cases the permission may be greatly different from allowing to make transactions, they could be permissions to view/add/edit/delete customer accounts/users of other customers for example.

HOW TO FIX:
	Implement logic to check permissions for requests. In the BankApp, when a users tries to make a transaction, the HasPermission() method is called, checking whether user has the permission to make a transaction. Other examples could be permissions view certain pages, make certain requests, start certain background jobs, access certain database tables.




### FLAW 3: A03:2021 – Injection

SPECIFIC ISSUES:
	CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')

CODE SOURCE:
	L150 - L164 views.py
https://github.com/jdeksnys/OWASP-top-ten-selected/blob/5d531f1873cde9882f6faf9f8a32c8683e569427/BankApp/views.py#L150-L164

DESCRIPTION:
	In the BankApp, a log entry is created when a transaction is made. The user can specify the message (text input) of the log entry. If a plain SQL query is used to insert a new log entry with the message from the user input, and the message is not escaped for possible SQL queries, the user can input a harmful query as a transaction message. For example, a harmful message in the BankApp could be (try after some transactions already made, to see change in messages):

harmful_query_after_this_message'); UPDATE BankApp_transactionhistory SET Message = 'THIS GOT HACKED!!!';--

The injected query ends the intended Insert query [with "');"], updates all messages (or do any other harmful query), and comments out any remaining parts of the intended query [with "--"].


HOW TO FIX:
	Sanitise the SQL query - do not execute a raw non-parametrised SQL query, but use the Django ORM. In the ORM, a query's SQL code is defined separately from the query's parameters and are escaped by the database driver [11]. Hence, the harmful message would just be inserted, but not executed.
	



### FLAW 4: A09:2021 – Security Logging and Monitoring Failures

SPECIFIC ISSUES:
	CWE-778: Insufficient Logging [9], CWE-223: Omission of Security-relevant Information [10]

CODE SOURCES:
	L17 - L18 views.py
https://github.com/jdeksnys/OWASP-top-ten-selected/blob/5d531f1873cde9882f6faf9f8a32c8683e569427/BankApp/views.py#L17-L18
	L97-L99 views.py
https://github.com/jdeksnys/OWASP-top-ten-selected/blob/5d531f1873cde9882f6faf9f8a32c8683e569427/BankApp/views.py#L97-L99
	L132-L133 views.py
https://github.com/jdeksnys/OWASP-top-ten-selected/blob/5d531f1873cde9882f6faf9f8a32c8683e569427/BankApp/views.py#L132-L133
	L137-L139 views.py
https://github.com/jdeksnys/OWASP-top-ten-selected/blob/5d531f1873cde9882f6faf9f8a32c8683e569427/BankApp/views.py#L137-L139


DESCRIPTION:
	Without logging or monitoring, breaches cannot be detected, hence no possibility to respond in real time, fix or learn from mistakes in the future. Problems include: no logging for security critical events (ex: login attempts, certain requests), no information for identifying the source or nature of attack or determining if the action is safe, which could allow the attacks to continue in the system without notice [10].

HOW TO FIX:
	Add logging for security critical events (ex: login attempts, permissions, transfers in BankApp). Include in the log: log-level, exact time, function called or code source, relevant variables, IP address or other security relevant information. See code sources for implementation.
	Moreover, analyse the logs or send notifications (ex: email, admin system dashboard) when unusual activity is detected. For instance during unusually large traffic flows, unusually many requests from single IP address or single user or unusual requests. In the BankApp, the implementation for the analysis of logs and notifications is omitted because it is outside the scope of this course, however it should be implemented in real world production systems.
	



### FLAW 5: A05:2021 – Security Misconfiguration

SPECIFIC ISSUE:
	CWE-756 Missing Custom Error Page [2]

CODE SOURCES:
	L33-L35 urls.py
https://github.com/jdeksnys/OWASP-top-ten-selected/blob/5d531f1873cde9882f6faf9f8a32c8683e569427/BankApp/urls.py#L33-L35
	L114 - L115 settings.py
https://github.com/jdeksnys/OWASP-top-ten-selected/blob/5d531f1873cde9882f6faf9f8a32c8683e569427/BankApp/settings.py#L114-L115

DESCRIPTION:
	Debug style error pages during raised exceptions may possibly expose sensitive information. Therefore, attackers could leverage additional information to mount attacks targeted at the framework, database or other resources [2].

HOW TO FIX:
	For server-side runtime errors, create generic error view (which does not disclose code) and map it in urls.py by setting the handler404 variable. Note: works when DEBUG=False. The error page should be shown if any non exiting page is requested, for unauthorized a different view can be shown. See code sources for implementation.




REFERENCES
[1] Common Weakness Enumeration. CWE-1216 Lockout Mechanism Errors. https://cwe.mitre.org/data/definitions/1216.html  
[2] Common Weakness Enumeration. CWE-756: Missing Custom Error Page. https://cwe.mitre.org/data/definitions/756.html  
[3] Common Weakness Enumeration. CWE-20: Improper Input Validation. https://cwe.mitre.org/data/definitions/20.html  
[4] Common Weakness Enumeration. CWE-87: Improper Neutralization of Alternate XSS Syntax. https://cwe.mitre.org/data/definitions/87.html
[5] Common Weakness Enumeration. CWE-74: Improper Neutralization of Special Elements in Output Used by a Downstream Component ('Injection'). https://cwe.mitre.org/data/definitions/74.html  
[6] Common Weakness Enumeration. CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting'). https://cwe.mitre.org/data/definitions/79.html  
[7] Common Weak Enumeration. CWE-80: Improper Neutralization of Script-Related HTML Tags in a Web Page (Basic XSS). https://cwe.mitre.org/data/definitions/80.html  
[8] Common Weak Enumeration. CWE-285: Improper Authorization. https://cwe.mitre.org/data/definitions/285.html  
[9] Common Weak Enumeration. CWE-778: Insufficient Logging. https://cwe.mitre.org/data/definitions/778.html  
[10] Common Weak Enumeration. CWE-223: Omission of Security-relevant Information. https://cwe.mitre.org/data/definitions/223.html  
[11] Django. Security in Django. https://docs.djangoproject.com/en/4.2/topics/security/  
