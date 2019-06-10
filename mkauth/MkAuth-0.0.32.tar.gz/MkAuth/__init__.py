import essentials
import json
import os
import datetime
from future.standard_library import install_aliases
from flask import Flask, make_response, redirect, request, send_file, abort

def ActivateMkAuth(config={}):
    global MkAuthSessionStorage, MkAuthSessionType, MkAuthActivated, MkAuthSessions
    """Use this to activate and configure MkAuth. MkAuth will not run unless this function is ran."""
    if "storage" in config:
        MkAuthSessionStorage = config['storage']
    if "type" in config:
        MkAuthSessionType = config['type']
    MkAuthActivated = True
    if MkAuthSessionStorage != False:
        try:
            MkAuthSessions = json.loads(essentials.Base64ToString(essentials.read_file("MkAuth/Sessions.info")))
        except:
            os.makedirs("MkAuth", exist_ok=True)
    print("MkAuth Activated")

MkAuthSessions = {}

def ValidateSession(request, invalidateType=['duration', 'ip']):
    if MkAuthActivated == False:
        raise EnvironmentError("MkAuth was not activated. Please use ActivateMkAuth(config) to activate.")
    try:
        MkAuthT = essentials.DictHeaders(request)['MkAuthT']
    except:
        try:
            MkAuthT = request.cookies['MkAuthT']
        except:
            return False
    try:
        MkAuthUserSession = MkAuthSessions[MkAuthT]
    except:
        return False
    if (essentials.TimeStamp() - MkAuthUserSession.Logon) > MkAuthUserSession.ActiveDuration and 'duration' in invalidateType:
        return False
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        MkTempRemoteIPAddress = request.environ['REMOTE_ADDR']
    else:
        MkTempRemoteIPAddress = request.environ['HTTP_X_FORWARDED_FOR']
    if MkTempRemoteIPAddress != MkAuthUserSession.IPAddress and 'ip' in invalidateType:
        return False
    return MkAuthSessions[MkAuthT]

def MakeResponse(response, request=None, isJson=False, extendSession=False, extensionPeriod=15):
    if isJson:
        response = json.dumps(response)
    resp = make_response(response)
    if extendSession:
        resp.set_cookie('MkAuthT', GetUserSession(request).Token, max_age=extensionPeriod*60)
    return resp

def NewAccount(username, password, access="basic"):
    """Make an encrpyted account file for a user
    dir: Directory the account file is to be kept. Ex. 'Accounts/[username]' - required
    username: The users username - required
    password: The users password - required
    access: a string/list/object attached to the user, for your use"""
    if MkAuthActivated == False:
        raise EnvironmentError("MkAuth was not activated. Please use ActivateMkAuth(config) to activate.")
    try:
        AccountData = essentials.read_json("MkAuth/Accounts.info")
    except:
        AccountData = {}
    if username in AccountData:
        raise ValueError("User already exists")
    VerTokes =[]
    for Account in AccountData:
        try:
            VerTokes.append(AccountData[Account]['VerifyToken'])
        except:
            pass
    essentials.CreateToken(32)
    MkTempData = {
        "account": username,
        "password": password,
        "created": essentials.TimeStamp(),
        "createdR": essentials.ReadableTime(),
        "login": True,
        "access": access,
        "masterToken": essentials.CreateToken(70),
        "Verified": False,
        "Meta": {},
        "VerifyToken": essentials.CreateToken(40, VerTokes),
        "devices": {}
    }
    AccountData[username.lower()] = MkTempData
    AccountData[username.lower()]['password'] = essentials.EncodeWithKey(password, password)
    essentials.write_json("MkAuth/Accounts.info", AccountData)
    return MkTempData

def VerifyAccount(VerifyToken):
    AccountData = essentials.read_json("MkAuth/Accounts.info")
    IsVeri = False
    Accounts = ""
    for Account in AccountData:
        if 'VerifyToken' in AccountData[Account]:
            if AccountData[Account]['VerifyToken'] == VerifyToken:
                Accounts = Account
                AccountData[Account]['Verified'] = True
                AccountData[Account]['VerifiedD'] = essentials.ReadableTime()
                AccountData[Account]['VerifiedT'] = essentials.TimeStamp()
                del AccountData[Account]['VerifyToken']
                IsVeri = True
    if IsVeri:
        essentials.write_json("MkAuth/Accounts.info", AccountData)
        return IsVeri, AccountData[Accounts]
    return IsVeri

def ChangePassword(username, newpassword, password="", masterToken=""):
    if MkAuthActivated == False:
        raise EnvironmentError("MkAuth was not activated. Please use ActivateMkAuth(config) to activate.")
    try:
        AccountData = essentials.read_json("MkAuth/Accounts.info")
    except:
        return {"Status": False}
    if username not in AccountData:
        return {"Status": False}
    data = AccountData[username]
    if password != "" and masterToken == "":
        if 'password' not in data:
            return {"Status": False}
        against = essentials.DecodeWithKey(password, data['password'])
        if against != password:
            return {"Status": False}
    if password == "" and masterToken != "":
        if "masterToken" not in data:
            return {"Status": False}
        if masterToken != data['masterToken']:
            return {"Status": False}
    if password == "" and masterToken == "":
        return {"Status": False}
    AccountData[username]['password'] = essentials.EncodeWithKey(password, password)
    essentials.write_json("MkAuth/Accounts.info", AccountData)
    return {"Status": data['login'], "Username": username, "data": data}

def UserLogin(username, password):
    username = username.lower()
    if MkAuthActivated == False:
        raise EnvironmentError("MkAuth was not activated. Please use ActivateMkAuth(config) to activate.")
    try:
        AccountData = essentials.read_json("MkAuth/Accounts.info")
    except Exception as e:
        print(e)
        return {"Status": False}
    if username not in AccountData:
        return {"Status": False}
    try:
        data = AccountData[username]
    except Exception as e:
        print(e)
        return {"Status": False}
    if 'password' not in data:
        return {"Status": False}
    against = essentials.DecodeWithKey(password, data['password'])
    if against != password:
        return {"Status": False, "Username": username}
    return {"Status": data['login'], "Username": username, "data": data}

TempAccountShortCuts = {}
def TempAccountToken(account="", token="", uses=1):
    if account != "" and token == "":
        key = essentials.CreateToken(30, TempAccountShortCuts)
        TempAccountShortCuts[key] = {
            "account": account,
            "uses": uses
        }
        return key
    if account == "" and token != "":
        try:
            account = TempAccountShortCuts[token]
            if account['uses'] == 0:
                del TempAccountShortCuts[token]
                return False
            TempAccountShortCuts[token]['uses'] -= 1
            return account['account']
        except:
            return False
    return False

def TrustDevice(request, account, DToken):
    try:
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            MkTempRemoteIPAddress = request.environ['REMOTE_ADDR']
        else:
            MkTempRemoteIPAddress = request.environ['HTTP_X_FORWARDED_FOR']
        AccountData = essentials.read_json("MkAuth/Accounts.info")
        try:
            CToken = request.cookies['MkAuthD']
            AccountData[account]['devices'][DToken]['TrustedByDevice'] = CToken
        except:
            pass
        AccountData[account]['devices'][DToken]["TrustedTS"] = essentials.TimeStamp()
        AccountData[account]['devices'][DToken]["Trusted"] = True
        AccountData[account]['devices'][DToken]["TrustedR"] = essentials.TimeStamp()
        AccountData[account]['devices'][DToken]['TrustedByIP'] = MkTempRemoteIPAddress
        essentials.write_json("MkAuth/Accounts.info", AccountData)
    except Exception as e:
        print(e)
        return False
    return True

def GetDevice(request):
    return GetUserSession(request).Devices[request.cookies['MkAuthD']]
    
def RequestLogin(request, Ltype, LoggedInRedirect, FailureRedirect, UserNonExistingRedirect, CheckVerified=False, Premissions=[], ActiveDuration=15,  AllowUntrustedDevices=False,  NewDeviceActionDef=""):
    ReqArgs = essentials.DictArgs(request)
    if "os" in ReqArgs:
        OS = ReqArgs['os']
    else:
        OS = "UnKnown"
    
    if Ltype == "form":
        creds = essentials.DictForm(request)
        
    if Ltype == "data":
        creds = essentials.DictData(request)
        
    if Ltype == "headers":
        creds = essentials.DictHeaders(request)

    if Ltype == "args":
        print("Using args is very unsafe. Please revert from using this, ever.")
        creds = essentials.DictArgs(request)
        
    Auth = UserLogin(creds['MkUsername'], creds['MkPass'])

    if 'Username' not in Auth:
        try:
            return redirect(UserNonExistingRedirect(creds['MkUsername']))
        except:
            return redirect(UserNonExistingRedirect)

    if Auth['Status'] == False:
        try:
            return redirect(FailureRedirect(Auth['Username']))
        except:
            return redirect(FailureRedirect)

    UserSes = UserSession(request, creds['MkUsername'], Auth['data'],  Premissions, ActiveDuration)
    try:
        resp = make_response(redirect(LoggedInRedirect(creds['MkUsername'])))
    except:
        resp = make_response(redirect(LoggedInRedirect))
    resp.set_cookie('MkAuthT', UserSes.Token, max_age=ActiveDuration*60)
    try:
        essentials.DictHeaders(request)['MkAuthD']
    except:
        try:
            if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
                MkTempRemoteIPAddress = request.environ['REMOTE_ADDR']
            else:
                MkTempRemoteIPAddress = request.environ['HTTP_X_FORWARDED_FOR']
            DToken = request.cookies['MkAuthD']
            AccountData = essentials.read_json("MkAuth/Accounts.info")
            AccountData[UserSes.User]['devices'][DToken]["LastUseTS"] = essentials.TimeStamp()
            AccountData[UserSes.User]['devices'][DToken]["LastUseR"] = essentials.ReadableTime()
            AccountData[UserSes.User]['devices'][DToken]['LastIP'] = MkTempRemoteIPAddress
            AccountData[UserSes.User]['devices'][DToken]['OS'] = OS
            essentials.write_json("MkAuth/Accounts.info", AccountData)
        except:
            if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
                MkTempRemoteIPAddress = request.environ['REMOTE_ADDR']
            else:
                MkTempRemoteIPAddress = request.environ['HTTP_X_FORWARDED_FOR']
            DToken = essentials.CreateToken(10)
            expire_date = datetime.datetime.now()
            expire_date = expire_date + datetime.timedelta(days=365)
            resp.set_cookie('MkAuthD', DToken, expires=expire_date)
            AccountData = essentials.read_json("MkAuth/Accounts.info")
            AccountData[UserSes.User]['devices'][DToken] = {
                "FirstUseR": essentials.ReadableTime(),
                "FirstUseTS": essentials.TimeStamp(),
                "ID": DToken,
                "OS": OS,
                "About": str(request.user_agent),
                "LastUseTS": essentials.TimeStamp(),
                "LastUseR": essentials.ReadableTime(),
                "FirstIP": MkTempRemoteIPAddress,
                "Trusted": False
            }
            essentials.write_json("MkAuth/Accounts.info", AccountData)
    if AllowUntrustedDevices == False and AccountData[UserSes.User]['devices'][DToken]['Trusted'] == False:
        try:
            resp = make_response(redirect(NewDeviceActionDef(UserSes.User, AccountData[UserSes.User]['devices'][DToken], request)))
            expire_date = datetime.datetime.now()
            expire_date = expire_date + datetime.timedelta(days=365)
            resp.set_cookie('MkAuthD', DToken, expires=expire_date)
            return resp
        except:
            return redirect(FailureRedirect)

    if NewDeviceActionDef != "":
        NewDeviceActionDef(UserSes.User, AccountData[UserSes.User]['devices'][DToken], request)
        
    return resp

def returnAlert(message, redir):
    return "<script>alert('" + message + "'); window.location = '" + redir + "'</script>"

def returnConfirm(message, accept, reject):
    return "<script>if confirm('" + message + "') {window.location = '" + accept + "'} else {window.location = '" + reject + "'}</script>"

def GetUserSession(request):
    try:
        return MkAuthSessions[essentials.DictHeaders(request)['MkAuthT']]
    except:
        try:
            return MkAuthSessions[request.cookies['MkAuthT']]
        except:
            raise ConnectionRefusedError("No Auth Token Found")

def UserLogout(request, redir):
    resp = make_response(redirect(redir))
    resp.set_cookie('MkAuthT', "", max_age=0)
    try:
        del MkAuthSessions[GetUserSession(request).Token]
    except:
        pass
    return resp

def setMeta(UserSess, newMeta):
    AccountData = essentials.read_json("MkAuth/Accounts.info")
    AccountData[UserSess.User]['Meta'] = newMeta
    essentials.write_json("MkAuth/Accounts.info", AccountData)
    return AccountData[UserSess.User]

class UserSession:
    def __init__(self, request, Username, accountData, premissions=[], ActiveDuration=15):
        """For Use With Python Flask
        request: the Flask - required
        premissions: a list of premissions attached to the session - optional
        ActiveDuration: Duration, in minutes, of how long you want the session to still be valid. - defaults to 15 minutes"""
        if MkAuthActivated == False:
            raise EnvironmentError("MkAuth was not activated. Please use ActivateMkAuth(config) to activate.")
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            MkTempRemoteIPAddress = request.environ['REMOTE_ADDR']
        else:
            MkTempRemoteIPAddress = request.environ['HTTP_X_FORWARDED_FOR']
        self.IPAddress = MkTempRemoteIPAddress
        self.Premissions = premissions
        self.Logon = essentials.TimeStamp()
        self.User = Username
        self.Devices = accountData['devices']
        self.DeviceInfo = str(request.user_agent)
        newDevice = False
        try:
            essentials.DictHeaders(request)['MkAuthD']
        except:
            try:
                request.cookies['MkAuthD']
            except:
                newDevice = True
        self.newDevice = newDevice
        if newDevice == False:
            self.Device = accountData['devices'][request.cookies['MkAuthD']]
        self.meta = accountData['Meta']
        self.ActiveDuration = ActiveDuration * 60
        self.Token = "MkA_" + essentials.CreateToken(32)
        try:
            self.userAgent = str(essentials.DictHeaders(request)["user-agent"])
        except:
            self.userAgent = "Unknown"
        MkAuthSessions[self.Token] = self

    def CheckDuration(self):
        return (self.Logon + self.ActiveDuration) - essentials.TimeStamp()

MkAuthSessionStorage = True
MkAuthSessionType = "token"
MkAuthActivated = False
