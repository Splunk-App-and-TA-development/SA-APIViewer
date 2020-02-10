import sys
import json
import requests
import base64
import csv
from collections import defaultdict
import splunk.entity as entity
import splunk.Intersplunk as si

def getArgs():
    fields, argvals = si.getKeywordsAndOptions()
    url = argvals.get("url","null")
    username = argvals.get("username","null")
    if url == 'null':
        url = "https://api.github.com/feeds"
    return url,username


def getCredentials(sessionKey, usernama):
    myapp = 'apicall_command'
    entities = entity.getEntities(['admin', 'passwords'], namespace=myapp, owner='nobody', sessionKey=sessionKey)

    for i, c in entities.items():
        if c['username']==username:
            return c['username'], c['clear_password']
        
def getSessionKey():

    results,dummyresults,settings = si.getOrganizedResults()
    sessionKey = settings.get("sessionKey", None)
    if len(sessionKey) == 0:
        sys.stderr.write("Did not receive a session key from splunkd. " +
                        "Please enable passAuth in inputs.conf for this " +
                        "script\n")
        exit(2)
    return sessionKey

def flatten_json(data):
    result = defaultdict(list)

    def flatten(x, name=""):
        if type(x) is dict:
            for k, v in x.items():
                flatten(v, k)
        elif type(x) is list:
            for v in x:
                flatten(v, name)
        else:
            result[name].append(x)

    flatten(data)
    max_length = max([len(v) for v in result.values()])

    for v in result.values():
        if max_length - len(v) == 1:
            v.insert(0, "")

        v.extend([v[-1]] * (max_length - len(v)))

    return result

url,username=getArgs()
header={'accept': "application/json"}
if username!='null':
    sessionKey = getSessionKey()
    username, password = getCredentials(sessionKey, username)
    usrPass = username + ':' + password
    b64Val = base64.b64encode(usrPass)
    header={"Authorization": "Basic %s" % b64Val, 'accept': "application/json"}

r=requests.request("GET", url, headers=header)
obj = json.loads(r.text)

flatjson = flatten_json(obj)
headerrow = ','.join(map(str, flatjson.keys()))
print(headerrow)
valuelist =  list(flatjson.values())
for i in range(len(valuelist[0])):
    row = ''
    for j in range(len(flatjson.keys())):
        row = row + ',' + str(valuelist[j][i]).replace('\n', '').replace('\r\n','')
    row = row[1:]    
    print(row)