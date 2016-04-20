GSENHA
======
GSenha is a front-end for [GSenha-API](https://github.com/globocom/gsenha-api). It provides a easy-to-use interface and abstraction of some actions for the user, like decrypting your passwords. 

Healthcheck:
-----------

There is a healthcheck, it tests the API's healthcheck.

	curl [GSENHA]/healthcheck

	Response: WORKING

Deploy:
------

There are multiple ways to run a Flask application, you can visit the [Flask official documentation for deployment](http://flask.pocoo.org/docs/0.10/deploying/).

It was tested with Ngnix + Gunicorn on a Ubuntu (14.04.3) server. First install all required python libraries (pip install -r requirements.txt).

You should also set some environment variables:

* BASE_URL="https://gsenha.example.com" (this should be whatever you setted to be the name)
* SECRET_KEY= a complex secret key

All the following should be the name you decided for the API. 

* API_HEALTHCHECK="https://gsenha-api.example.com/healthcheck"
* URL_GSENHA_ADDFOLDER="https://gsenha-api.example.com/add/folder"
* URL_GSENHA_ADDPERSONAL="https://gsenha-api.example.com/add/password/personal"
* URL_GSENHA_ADDPERSONALEXTERNAL="https://gsenha-api.example.com/add/password/personal/external"
* URL_GSENHA_ADDSHARED="https://gsenha-api.example.com/add/password/shared"
* URL_GSENHA_ADDSHAREDEXTERNAL="https://gsenha-api.example.com/add/password/shared/external"
* URL_GSENHA_DELFOLDER="https://gsenha-api.example.com/delete/folder"
* URL_GSENHA_DELPASSWORD="https://gsenha-api.example.com/delete/password"
* URL_GSENHA_GETFOLDERS="https://gsenha-api.example.com/get/folders"
* URL_GSENHA_GETGROUPS="https://gsenha-api.example.com/get/groups"
* URL_GSENHA_GETMYGROUPS="https://gsenha-api.example.com/get/mygroups"
* URL_GSENHA_GETTREE="https://gsenha-api.example.com/get/tree"
* URL_GSENHA_LOGIN="https://gsenha-api.example.com/login"
* URL_GSENHA_PASSWORDS="https://gsenha-api.example.com/get/passwords"
* URL_GSENHA_UNLOCK2="https://gsenha-api.example.com/unlocking"
* URL_GSENHA_UNLOCK="https://gsenha-api.example.com/unlock"
* URL_GSENHA_UPDATEPASSWD="https://gsenha-api.example.com/update/password"
* URL_GSENHA_UPDATEPUBKEY="https://gsenha-api.example.com/update/publickey"
* URL_GSENHA_USER="https://gsenha-api.example.com/add/user"

Architecture:
----------------------

All communication must be over TLS. You should not use a self-signed certificate. In every request from the front-end to the API the certificate is verified. If the verification fails the request will not work.

![alt text](docs/images/diagram_gsenha.png)

Logs:
----

All requests are logged in this format:
	
	In case of success:
		action=|api path| user=|username| src=|source address| result=|success|

	In case of failure:
		action=|api path| desc=|error description| result=|error| user=|username| src=|source address|

All logs are sent to stdout.

User guide:
=============================

Login:
------

If you are already a member just go to login page and use your LDAP's credentials and your private key (**IT WILL NEVER LEAVE YOUR BROWSER**).

![alt text](docs/images/login.png)

If you are not a member yet you must have a key pair. In order to generate it:

Private key:

$ openssl genrsa -out privkey.pem 4096

![alt text](docs/images/privkey.png)

The file should be named "privkey.pem" and should begins with "-----BEGIN RSA PRIVATE KEY-----" and ends with "-----END RSA PRIVATE KEY-----".

and the public key:

$ openssl rsa -in privkey.pem -outform PEM -pubout -out public.pem

![alt text](docs/images/pubkey.png)

The file should be named "public.pem" and should begins with "-----BEGIN PUBLIC KEY-----" and ends with "-----END PUBLIC KEY-----".

After generating your key pair you can add yourself. Your username and password should be the same as your LDAP's credentials. 

![alt text](docs/images/adduser.png)

If everything went fine you are now able to login.

Main page:
----------

![alt text](docs/images/login2.png)

On the navbar on top of the page you can see all actions available, and in the tree directory it is possible to see all your passwords. 

Adding a password:
-----------------

You can go to "Add Password" on the navbar, there are four types of password addition.

* **Personal** : it will add a personal password, only yourself will be able to see this password. It should be added in a personal folder.
* **Group** : it will add a shared password in the chosen group. All members will be able to see this password. It should be added in a shared folder.
* **To other user** : it will add a password for a specified user, not for yourself. Only him/her will be able to see it.
* **To other group** : it will add a password for a specified group you are not a member of. All members of that group will be able to see the password.

![alt text](docs/images/addpasswd.png)

Choosing one of the four types of password addition will get you to a form like in the image below.

![alt text](docs/images/addpasswd2.png)


It is possible to generate a random password, just click on "Gen. Passwd" button. Select the password length and click on "Generate" button.

![alt text](docs/images/generatepasswd.png)

Selecting a password:
------------------------

Click on the password's name on the directory tree and a panel will be prompted on the right side with the password and its metadata. The password will be offuscated, to see it in clear text click on the eye button. You can copy it to clipboard hitting the arrow button.
 
![alt text](docs/images/passwd.png)

![alt text](docs/images/passwd2.png)

![alt text](docs/images/clearpasswd.png)

You can search a password on the search field above the directory tree, if matched it will be highlithed in red.  

Deleting a password:
-----------------

To delete a password just click on "Delete" button. You must confirm to delete it. 

Shared passwords will be deleted for all users.

![alt text](docs/images/delpasswd.png)

Adding and removing folders:
---------------------------

You can add and delete folders. Go to "Folders" on the navbar and select add or delete. 

![alt text](docs/images/folder.png)

You just need to choose the path and a name for the folder. 

![alt text](docs/images/addfolder.png)

To remove just select the folder, it must be empty.

Atualizar chave pública:
------------------------

It is possible to change your public key. Remember that after changing it, you will have to use your new private key. If you decide to change your public key you should NOT one that have already been used. 

![alt text](docs/images/updatepubkey.png)

Unlocking a new user:
---------------------

A new user will not be able to see the previously added passwords in a group. An older member have to unlock this new user. This old member have to go to "Unlock User" on the navbar, select the group and the new user.

![alt text](docs/images/unlock.png)

It may take some time, it will depend on how many passwords there are in this group.

Import passwords:
----------------

It is possible to import passwords from a password manager. Just go to "Import" and see the supported files and how they will be interpreted. 

![alt text](docs/images/import.png)

Export personal passwords:
-------------------------

To backup your passwords you can click on "Export" and a .csv file will be generated with your personal password in clear text, this file can be imported by Password Safe / Password Gorilla.