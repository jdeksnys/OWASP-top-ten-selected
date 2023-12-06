from asyncio.log import logger
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from BankApp.Services.authenticationService import HandleFailedLogin, GetCustomer, ResetFailedLoginCount, HasPermission
from BankApp.models import Account, TransactionHistory
from django.db import transaction, connection
from django.conf import settings
import logging
import json
import sqlite3

if(settings.IS_SECURE):
	logger = logging.getLogger("django")

def errorView(request, exception):
	if(settings.IS_SECURE):# SECURE IF LOGGING INVALID URLS
		logger.info(f"Attempted to access invalid url {request.build_absolute_uri()}")
	return render(request, "Views/error.html")

def LoginView(request):
	if (request.method == "POST"):
		try:
			socSecNumber = int(request.POST.get("username"))
			_password = request.POST.get("password")
		except:
			return render(request, "Views/login.html", {"message": ["Username or password incorrect"]})
		customer = GetCustomer(socSecNumber)
		user = authenticate(request, SocSecNumber=socSecNumber, password=_password)
		
		if(user is not None):
			login(request, user)
			ResetFailedLoginCount(customer)
			return redirect('/')
		else:
			# NOT SECURE IF NO LOGIN RESTRICTIONS:
			if(not settings.IS_SECURE):
				return render(request, "Views/login.html", {"message": json.dumps(["Username or password incorrect"])})
			# SECURE IF SIGN IN ATTEMPTS LIMITED WITH EXPONENTIAL LOCK-TIME:
			elif(settings.IS_SECURE):
				result = HandleFailedLogin(customer)
				if(result["usernameOk"]):
					if(result["isTimeLocked"]):	
						return render(request, "Views/login.html", {"message": [f"Exceeded number of tries. Try again in {result['timeDelay']} seconds"], "disabled": result["disabled"]})
				return render(request, "Views/login.html", {"message": ["Username or password incorrect"], "disabled": result["disabled"]})

	else:
		return render(request, "Views/login.html")


def LogoutView(request):
	logout(request)
	return redirect('/')


@login_required
def IndexView(request):
	custFromId = request.user.Id
	accFrom = Account.objects.filter(CustomerId = custFromId).first()
	balance = round(accFrom.Balance, 2)

	accToList = Account.objects.exclude(CustomerId = custFromId)
	errorMsg = request.session.get("errorMsg")
	message = request.session.get("message")

	data = {
		"name": request.user.FirstName,
		"balance": balance,
		"accountFrom": accFrom,
		"accountsTo": accToList,
		"errorMsg": errorMsg,
		"message": message
	}
	request.session['errorMsg'] = None
	return render(request, "Views/index.html", data)


def login_user(request):
	if (request.method == "POST"):
		username = request.POST.get("username")
		password = request.POST.get("password")
		user = authenticate(request, username=username, password=password)
		if(user is not None):
			login(request, user)
			return render(request, "Views/index")
		return render(request, "Views/error")
	else:
		return render(request, "Views/login")


@login_required
def TransferView(request):
	# NOT SECURE: no authorization (no user permission validation for requests)
	# SECURE IF USER PERMISSION FOR REQUESTS CHECKED:
	if(settings.IS_SECURE):
		if(not HasPermission(request.user.Id, "can_transfer")):
			# SECURE IF LOGGING UNAUTHORIZED REQUESTS
			if(settings.IS_SECURE):
				logger.warning(f"Customer {request.user.Id} attempted unauthorised transaction.")
			request.session['errorMsg'] = "Transaction failed. User missing permissions."
			return redirect("/");

	accFromId = request.POST.get("accountFromId")
	accToId = request.POST.get("accountToId")
	message = request.POST.get("message")

	if(accFromId == None):
		request.session['errorMsg'] = "Transaction failed. Sender account not selected."
		return redirect("/");
	if(accToId == None):
		request.session['errorMsg'] = "Transaction failed. Receiver account not selected."
		return redirect("/");
	
	accFromId = int(accFromId)
	accToId = int(accToId)
	amount_val = str(request.POST.get("amount"))
	amount_val = amount_val.replace(",", ".")
	try:
		amount = float(amount_val)
	except Exception:
		request.session['errorMsg'] = "Transaction failed. Invalid amount: please enter numeric value."
		return redirect("/");

	accTo = Account.objects.get(Id = accToId)
	accFrom = Account.objects.get(Id = accFromId)
	accFromBalance = accFrom.Balance
	
	if(accFromId == accToId):
		request.session['errorMsg'] = "Transaction failed. Cannot transfer to same account."
		return redirect("/");
	if(amount <= 0):
		if(settings.IS_SECURE):# SECURE IF LOGGING UNUSUAL REQUESTS
			logger.warning(f"Customer {request.user.Id} transaction failed. Attempted negative transfer amount.")
		request.session['errorMsg'] = "Transaction failed. Amount must be positive."
		return redirect("/");
	if(accFromBalance < amount):
		# SECURE IF LOGGING UNUSUAL REQUESTS
		if(settings.IS_SECURE):
			logger.warning(f"Customer {request.user.Id} transaction failed. Insufficient funds.")
		request.session['errorMsg'] = "Transaction failed. Insufficient funds."
		return redirect("/");

	with transaction.atomic():
		accFrom.Balance -= amount
		accTo.Balance += amount
		accFrom.save()
		accTo.save()


	if(not settings.IS_SECURE):
		# NOT SECURE, SQL INJECTION POSSIBLE, HACKER CAN CHANGE/DELETE ALL MESSAGES IN DATABASE OR EXECUTE OTHER QUERIES:
		# EXAMPLE INJECTION (SQL):
		# harmful_query_after_this_message'); UPDATE BankApp_transactionhistory SET Message = 'THIS GOT HACKED!!!';--
		name = accTo.Name
		name = name.replace("\"", "")
		name = name.replace("'", "")
		sql2 = f"INSERT INTO BankApp_transactionhistory (AccountFrom_id, AccountToName, Amount, Message) VALUES ({accFromId}, '{name}', {amount}, '{message}');"

		conn = sqlite3.connect('BankAppDb.sqlite3')
		c = conn.cursor()
		c.executescript(sql2)
	else:
		# SECURE IF ORM USED (USES PARAMETRIZED QUERIES):
		TransactionHistory.objects.create(AccountFrom_id=accFromId, AccountToName=accTo.Name, Amount=amount, Message=message)

	transaction_history_logs = list(TransactionHistory.objects.filter(AccountFrom_id=accFromId).order_by('-id').values_list('AccountFrom_id', 'AccountToName', 'Amount', 'Message'))
	messages = [f"Transferred {log[2]}EUR to {log[1]} with message: {log[3]}" for log in transaction_history_logs]

	request.session['message'] = json.dumps(messages)
	if(settings.IS_SECURE):
		logger.info(f"Customer {request.user.Id} made transaction.")

	return redirect("/");