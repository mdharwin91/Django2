from ..model import models
from ..database import datacrud
from django.contrib.auth.hashers import check_password

class loginauth:
    def logon(a, b):
       userInfo = {}
       pk = pkFinder(a.upper())
       if not pk:
           userInfo['user'] = "ACCESS DENIED"
           return userInfo

       dbResponse = datacrud.get(pk, a.upper())
       if not dbResponse:
           userInfo['user'] = "ACCESS DENIED"
           return userInfo

       loginDict = dbResponse
       
       stored_password = loginDict.get("password")
       # Check if password matches (Supports both Hashed and Legacy Plain Text)
       is_valid_password = (stored_password and check_password(b, stored_password)) or (b == stored_password)

       if (a.upper() == loginDict.get("planner-sk")) and is_valid_password:
           userInfo['user'] = loginDict.get("name")
           userInfo['pk'] = loginDict.get("planner-pk")
           userInfo['sk'] = loginDict.get("planner-sk")
           return userInfo
       else:
           userInfo['user'] = "ACCESS DENIED"
           return userInfo   

def pkFinder (sk):
    if not isinstance(sk, str):
        return None
    if sk[0:3] == "TID":
        return "Teacher"
    elif sk[0:3] == "AID":
        return "Admin"