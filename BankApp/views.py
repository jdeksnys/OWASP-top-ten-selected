from asyncio.log import logger
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from BankApp.Services.authenticationService import HandleFailedLogin, GetCustomer, ResetFailedLoginCount, HasPermission
from BankApp.models import Account
from django.db import transaction
from django.conf import settings
import logging


if(settings.IS_SECURE):
	logger = logging.getLogger("django")


def errorView(request, exception):
	logger.info(f"Attempted to access invalid url {request.build_absolute_uri()}")
	return render(request, "Views/error.html")


def LoginView(request):
	if (request.method == "POST"):
		socSecNumber = int(request.POST.get("username"))
		_password = request.POST.get("password")

		customer = GetCustomer(socSecNumber)
		user = authenticate(request, SocSecNumber=socSecNumber, password=_password)
		
		if(user is not None):
			login(request, user)
			ResetFailedLoginCount(customer)
			return redirect('/')
		else:
			# NOT SECURE IF NO LOGIN RESTRICTIONS:
			if(not settings.IS_SECURE):
				return render(request, "Views/login.html", {"message": "Username or password incorrect"})
			# SECURE IF SIGN IN ATTEMPTS LIMITED WITH EXPONENTIAL LOCK-TIME:
			elif(settings.IS_SECURE):
				result = HandleFailedLogin(customer)
				if(result["usernameOk"]):
					if(result["isTimeLocked"]):	
						return render(request, "Views/login.html", {"message": f"Exceeded number of tries. Try again in {result['timeDelay']} seconds", "disabled": result["disabled"]})
				return render(request, "Views/login.html", {"message": "Username or password incorrect", "disabled": result["disabled"]})

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

	# NOT SECURE: no account validation
	# SECURE IF VALIDATION ADDED:
	if(settings.IS_SECURE):
		if(accFromId == None):
			request.session['errorMsg'] = "Transaction failed. Sender account not selected."
			return redirect("/");
		if(accToId == None):
			request.session['errorMsg'] = "Transaction failed. Receiver account not selected."
			return redirect("/");
	
	accFromId = int(accFromId)
	accToId = int(accToId)
	accFrom = Account.objects.get(Id = accFromId)
	accFromBalance = accFrom.Balance

	try:
		val = str(request.POST.get("amount"))
		val = val.replace(",", ".")
		amount = float(val)
	except Exception:
		request.session['errorMsg'] = "Transaction failed. Invalid amount: please enter numeric value."
		return redirect("/");

	# NOT SECURE: no validation for amount, accFromId and accToId
	# SECURE IF VALIDATION ADDED:
	if(settings.IS_SECURE):
		if(accFromId == accToId):
			request.session['errorMsg'] = "Transaction failed. Cannot transfer to same account."
			return redirect("/");
		if(amount <= 0):
			# SECURE IF LOGGING UNUSUAL REQUESTS
			if(settings.IS_SECURE):
				logger.warning(f"Customer {request.user.Id} transaction failed. Attempted negative transfer amount.")
			request.session['errorMsg'] = "Transaction failed. Amount must be positive."
			return redirect("/");
		if(accFromBalance < amount):
			# SECURE IF LOGGING UNUSUAL REQUESTS
			if(settings.IS_SECURE):
				logger.warning(f"Customer {request.user.Id} transaction failed. Insufficient funds.")
			request.session['errorMsg'] = "Transaction failed. Insufficient funds."
			return redirect("/");



	# NOT SECURE:
	if(not settings.IS_SECURE):
		accTo = Account.objects.get(Id = accToId)
		accFrom.Balance -= amount
		accTo.Balance += amount
		accFrom.save()
		accTo.save()
	# SECURE IF WRAPPED IN TRANSACTION:
	elif(settings.IS_SECURE):
		with transaction.atomic():
			accTo = Account.objects.get(Id = accToId)
			accFrom.Balance -= amount
			accTo.Balance += amount
			accFrom.save()
			accTo.save()

	request.session['message'] = f"Last transaction: Transfered funds with message: {message}"
	if(settings.IS_SECURE):
		logger.info(f"Customer {request.user.Id} made transaction.")

	return redirect("/");