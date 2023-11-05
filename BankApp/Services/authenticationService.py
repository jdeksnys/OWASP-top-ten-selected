from datetime import datetime, timedelta, tzinfo
from time import timezone
from xmlrpc.client import FastParser
from django.contrib.auth import authenticate
from BankApp.models import Customer, Permission, CustomerPermissions
from django.db.models import Exists, Q
from django.conf import settings
import logging


def GetCustomer(socSecNumber):
    try:
        customer = Customer.objects.get(SocSecNumber = socSecNumber)
        if(customer != None):
            return customer
    except:
        pass
    return None


def HandleFailedLogin(customer):
    if(customer != None):
        return IsTimeLocked(customer)
    return {"usernameOk": False}


def SetFailedLoginCount(customer):
    if (customer == None):
        return
    try:
        customer.FailedLoginCount += 1
        customer.last_login = datetime.now().replace(tzinfo=None)
        customer.save()
    except:
        pass


def ResetFailedLoginCount(customer):
    if (customer == None):
        return
    try:
        customer.FailedLoginCount = 0
        customer.last_login = datetime.now()
        customer.IsTimeLockedUntil = None
        customer.save()
    except:
        pass


def IsTimeLocked(customer):
    if(settings.IS_SECURE):
        logger = logging.getLogger("django")
    SetFailedLoginCount(customer)
    attempts = customer.FailedLoginCount

    timeLockedUntil = (customer.TimeLockedUntil if customer.TimeLockedUntil != None else datetime.now().replace(tzinfo=None))
    timeUntilUnlock = timeLockedUntil.timestamp() - datetime.now().replace(tzinfo=None).timestamp()
    timeDelay = 30 * 2 ** (attempts-2)

    if(attempts >= 3):
        # SECURE IF LOGGING FAILED ATTEMPTS
        if(settings.IS_SECURE):
            logger.warning(f"Customer {customer.Id} exceeded login attempts.")
        return {"usernameOk": True, "isTimeLocked":True, "timeDelay": timeDelay, "disabled": True}
    else:
        # SECURE IF LOGGING FAILED ATTEMPTS
        if(settings.IS_SECURE):
            logger.warning(f"Customer {customer.Id} over-attempted login {attempts} times.")

        lastLogin = (customer.last_login if customer.last_login != None else datetime.now().replace(tzinfo=None))
        customer.TimeLockedUntil = (lastLogin + timedelta(seconds=timeDelay)).replace(tzinfo=None)
        customer.save()
        return {"usernameOk": True, "isTimeLocked": False, "disabled": False}



def HasPermission(customerId, permCode):
    permissionId = Permission.objects.get(Code=permCode).Id
    if(customerId != None and permissionId != None):
        hasPermission = CustomerPermissions.objects.filter(Q(CustomerId=customerId) & Q(PermissionId=permissionId)).exists()
        return hasPermission
    return False;