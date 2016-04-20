# -*- coding: utf-8 -*-
import json, requests, sys, settings

class SendJson:

    def send_get_passwords(self,token):
        url_gsenha = settings.URL_GSENHA_PASSWORDS
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer}
        req = requests.get(url_gsenha, headers=headers, verify=True)
        return req

    def send_login(self,user,passwd):
        url_gsenha = settings.URL_GSENHA_LOGIN
        data = {}
        data["username"] = user
        data["password"] = passwd
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.post(url_gsenha, data=json.dumps(data), headers=headers, verify=True)
        return req

    def send_add_user(self,user,passwd,pk):
        url_gsenha = settings.URL_GSENHA_USER
        data = {}
        data["user"] = user
        data["password"] = passwd
        data["pubkey"] = pk
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.post(url_gsenha, data=json.dumps(data), headers=headers, verify=True)
        return req

    def send_add_password_personal(self,token,name,passwd,folder,login,url,description):
        url_gsenha = settings.URL_GSENHA_ADDPERSONAL
        data = {}
        data["name"] = name
        data["passwd"] = passwd
        data["folder"] = folder
        data["login"] = login
        data["url"] = url
        data["description"] = description
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer,'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.post(url_gsenha, data=json.dumps(data), headers=headers, verify=True)
        return req

    def send_add_password_personal_url(self,token,name,passwd,folder,login,description):
        url_gsenha = settings.URL_GSENHA_ADDPERSONAL
        data = {}
        data["name"] = name
        data["passwd"] = passwd
        data["folder"] = folder
        data["login"] = login
        data["description"] = description
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer,'Content-type': 'application/json', 'Accept': 'text/plain'}        
        req = requests.post(url_gsenha, data=json.dumps(data), headers=headers, verify=True)
        return req

    def send_add_password_group(self,token,name,passwd,folder,group,login,url,description):
        url_gsenha = settings.URL_GSENHA_ADDSHARED
        data = {}
        data["name"] = name
        data["passwd"] = passwd
        data["group"] = group
        data["folder"] = folder
        data["login"] = login
        data["url"] = url
        data["description"] = description
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer,'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.post(url_gsenha, data=json.dumps(data), headers=headers, verify=True)
        return req

    def send_add_password_group_url(self,token,name,passwd,folder,group,login,description):
        url_gsenha = settings.URL_GSENHA_ADDSHARED
        data = {}
        data["name"] = name
        data["passwd"] = passwd
        data["group"] = group
        data["folder"] = folder
        data["login"] = login
        data["description"] = description
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer,'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.post(url_gsenha, data=json.dumps(data), headers=headers, verify=True)
        return req

    def send_add_password_personal_ext(self,token,name,passwd,username,login,url,description):
        url_gsenha = settings.URL_GSENHA_ADDPERSONALEXTERNAL
        data = {}
        data["name"] = name
        data["passwd"] = passwd
        data["username"] = username 
        data["login"] = login
        data["url"] = url
        data["description"] = description
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer,'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.post(url_gsenha, data=json.dumps(data), headers=headers, verify=True)
        return req

    def send_add_password_personal_ext_url(self,token,name,passwd,username,login,description):
        url_gsenha = settings.URL_GSENHA_ADDPERSONALEXTERNAL
        data = {}
        data["name"] = name
        data["passwd"] = passwd
        data["username"] = username
        data["login"] = login
        data["description"] = description
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer,'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.post(url_gsenha, data=json.dumps(data), headers=headers, verify=True)
        return req

    def send_add_password_group_ext(self,token,name,passwd,group,login,url,description):
        url_gsenha = settings.URL_GSENHA_ADDSHAREDEXTERNAL
        data = {}
        data["name"] = name
        data["passwd"] = passwd
        data["group"] = group
        data["login"] = login
        data["url"] = url        
        data["description"] = description
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer,'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.post(url_gsenha, data=json.dumps(data), headers=headers, verify=True)
        return req

    def send_add_password_group_ext_url(self,token,name,passwd,group,login,description):
        url_gsenha = settings.URL_GSENHA_ADDSHAREDEXTERNAL
        data = {}
        data["name"] = name
        data["passwd"] = passwd
        data["group"] = group
        data["login"] = login
        data["description"] = description
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer,'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.post(url_gsenha, data=json.dumps(data), headers=headers, verify=True)
        return req

    def send_add_folder(self,token,path,name):
        url_gsenha = settings.URL_GSENHA_ADDFODLER
        data = {}
        data["path"] = path
        data["name"] = name
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer,'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.post(url_gsenha, data=json.dumps(data), headers=headers, verify=True)
        return req

    def send_del_folder(self,token,folder):
        url_gsenha = settings.URL_GSENHA_DELFOLDER
        data = {}
        data["folder"] = folder
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer,'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.post(url_gsenha, data=json.dumps(data), headers=headers, verify=True)
        return req        

    def send_get_folders(self,token):
        url_gsenha = settings.URL_GSENHA_GETFOLDERS
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer}
        req = requests.get(url_gsenha, headers=headers, verify=True)
        return req

    def send_get_groups(self,token):
        url_gsenha = settings.URL_GSENHA_GETGROUPS
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer}
        req = requests.get(url_gsenha, headers=headers, verify=True)
        return req

    def send_get_mygroups(self,token):
        url_gsenha = settings.URL_GSENHA_GETMYGROUPS
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer}
        req = requests.get(url_gsenha, headers=headers, verify=True)
        return req

    def send_get_tree(self,token):
        url_gsenha = settings.URL_GSENHA_GETTREE
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer}
        req = requests.get(url_gsenha, headers=headers, verify=True)
        return req

    def send_unlock(self,token,group,usertounlock):
        url_gsenha = settings.URL_GSENHA_UNLOCK
        data = {}
        data["group"] = group
        data["usertounlock"] = usertounlock
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer,'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.post(url_gsenha, data=json.dumps(data), headers=headers, verify=True)
        return req

    def send_unlock2(self,token,data):
        url_gsenha = settings.URL_GSENHA_UNLOCK2
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer,'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.post(url_gsenha, data=json.dumps(data), headers=headers, verify=True)
        return req

    def send_update(self,token,id_passwd,passwd,url,login,name,description):
        url_gsenha = settings.URL_GSENHA_UPDATEPASSWD
        data = {}
        data["id"] = id_passwd
        if passwd != None:
            data["passwd"] = passwd
        if url != None:
            data["url"] = url
        if login != None:
            data["login"] = login
        if name != None:
            data["name"] = name
        if description != None:
            data["description"] = description
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer,'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.post(url_gsenha, data=json.dumps(data), headers=headers, verify=True)
        return req

    def send_update_url(self,token,id_passwd,passwd,login,name,description):
        url_gsenha = settings.URL_GSENHA_UPDATEPASSWD
        data = {}
        data["id"] = id_passwd
        data["passwd"] = passwd
        data["login"] = login
        data["name"] = name
        data["description"] = description
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer,'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.post(url_gsenha, data=json.dumps(data), headers=headers, verify=True)
        return req

    def send_update_pubkey(self,token,pubkey,privkey):
        url_gsenha = settings.URL_GSENHA_UPDATEPUBKEY
        data = {}
        data["pubkey"] = pubkey
        data["privkey"] = privkey
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer,'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.post(url_gsenha, data=json.dumps(data), headers=headers, verify=True)
        return req

    def send_delete_password(self,token,idPassword):
        url_gsenha = settings.URL_GSENHA_DELPASSWORD
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer,'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.delete(url_gsenha+"/"+idPassword, headers=headers, verify=True)
        return req

    def send_import(self,token,data):
        url_gsenha = settings.URL_GSENHA_ADDPERSONAL
        bearer = "Bearer "+str(token)
        headers = {'Authorization':bearer,'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.post(url_gsenha, data=json.dumps(data), headers=headers, verify=True)
        return req        