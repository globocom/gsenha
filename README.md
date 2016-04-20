GSENHA API
==========

GSenha-API is a password manager, but not an usual one. Its architecture was designed to avoid information leakage in the case of a compromise. It is possible to store a password and share it among a group of users in a secure way, and also store a personal password, just for yourself. Storing a personal password is just like using another well-known password manager like KeePass, PasswordSafe, Password Gorilla and others. The goal in GSenha is to be able to store a password and allow other users to have access to it in a secure way, without backdoors and no shared secret keys. This is done with asymmetric cryptography (private and public keys).

GSenha-API works as a REST API with JWT. There is a front-end (GSenha), but anyone can write a custom one or use it as a command line tool. 

There is one dependency, you must have a LDAP base. GSenha does not perform user management, it uses the information provided in the LDAP base. Authentication and authorization are all handled by the LDAP. A new user must add herself/himself into the system informing his/her LDAP's credentials and a RSA public key. Gsenha will perform a query on the LDAP server and, once authentication is granted, all user information will be retrieved, like given name, surname, email, groups and it will be stored in a database with the public key. After that, the user will perform a login using his/her LDAP's credentials. In all requests of the API it will be performed a query into LDAP to see if there is any inconsistency with the user and his/her groups. The GSenha-API's database group table will mirror LDAP's base. This is how authorization is handled. 

Personal Passwords and Shared Passwords
---------------------------------------

As said before, it is possible to add personal and shared passwords. Personal passwords will be added into a personal folder as specified by the user. Only the user will be able to access this password. Shared passwords will be added into a shared folder and all members of the specified group will be able to access this passwords. 

A personal password is encrypted with the user's public key and stored in the database. A shared password is added n-times, where n is the number of users in the group, each one is encrypted with an user public key. In that way, all users from that group will have access to that password.

Private Keys
------------

The system will never get to know a user's private key. All the decryption process is made client-side. When requesting your passwords in the API, they will be retrieved encrypted, even its metadata, and the user needs to decrypt them. If you are using the front-end this is completely transparent for you. When performing the login, user will copy-and-paste the private key in the form, or select the private key's file. The private key is stored in the SesssionStorage of the browser, never being sent to the server.

Deploy
------

There are multiple ways to run a Flask application, you can visit the [Flask official documentation for deployment](http://flask.pocoo.org/docs/0.10/deploying/). 

It was tested with Ngnix + Gunicorn on a Ubuntu (14.04.3) server, and MySQL as database. To initialize the database, run the script "mysqlcreate" inside the script folder. Then install the required python libraries (pip install -r requirements.txt) and the OS packages (requirements.apt).

You should also set some environment variables:

* MYSQL_DBNAME=gsenha (or whatever if you changed the mysqlcreate script)
* MYSQL_HOST= your mysql endpoint
* MYSQL_USERNAME= mysql username
* MYSQL_PASSWORD= mysql unsername password
* LDAP_URI= your ldap endpoint, something like ldaps://ldap.example.com. You should (must) use ldapS.
* LDAP_USER= a ldap user, it can be a read-only user since gsenha will not write in ldap. Something like "cn=ldapuser,ou=User,dc=example,dc=com"
* LDAP_PASSWORD= ldap user password
* CERT= complete path to ldap certificate - Not mandatory
* CLIENT_CERT= complete path to ldap client certificate - Not mandatory
* CLIENT_KEY= complete path to ldap client key - Not mandatory
* BASE_GROUP_DN= your base group DN from ldap, something like "ou=Groups,dc=example,dc=com". 
* BASE_USER_DN= your base user DN from ldap, something like "ou=Users,dc=example,dc=com". 
* SECRET_KEY= a complex secret key
* SMTP_SERVER= your smtp server endpoint
* EMAIL_SENDER= the email that will be set as the sender, something like "gsenha@example.com"
* EMAIL_SENDER_NAME= the email sender name, something like "GSenha"


Logs
----

All requests are logged in this format:	
	
	In case of success:
		action=|api path| user=|username| src=|source address| result=|success|

	In case of failure:
		action=|api path| desc=|error description| result=|error| user=|username| src=|source address|

All logs are sent to stdout.

Architecture
------------

All communication must be over TLS. You should not use a self-signed certificate.

![alt text](docs/images/gsenhaapi.png)

Generating RSA keys 
-------------------

The RSA keys must be 4096 bits. 

Generating private key:
------------------------

	$ openssl genrsa -out privkey.pem 4096 

The generated file is your private key, its name will be "privkey.pem". Keep it secret!

The file should begins with "-----BEGIN RSA PRIVATE KEY-----" and ends with "-----END RSA PRIVATE KEY-----".

Generating public key:
________________________

	$ openssl rsa -in privkey.pem -outform PEM -pubout -out public.pem 

The generated file is your public key, its name will be "public.pem".

The file should begins with "-----BEGIN PUBLIC KEY-----" and ends with "-----END PUBLIC KEY-----".

This one will be informed when adding yourself.


Private key fallback
----------------------

The system is not able to retrieve your private key in case of loss. It is user's obligation to keep his/her private key safe. **DO NOT LOSE YOUR PRIVATE KEY!**

Healthcheck
-----------

There is a healthcheck in the API, it tests the connection with the LDAP and the database. 

Exemple with curl:

	curl [GSENHA_API]/healthcheck

	Answer: WORKING

API concepts
---

### Response results

All methods have a HTTP status code (200,400,403,500) and a JSON with some information.

	In case of success:

	{"status":"success","message":"message"}

	In case of error:

	{"status":"error","message":"error message"}

### Add a user (POST /add/user)

The user should add herself/himself.

Method: "/add/user"

Required JSON:

	{"user":"username","password":"password","pubkey":"user's public key"}

Usage example:

	$ curl -vvv -H "Content-Type: application/json" -d '{"user":"leopoldo","password":"pantera123","pubkey":
	"-----BEGIN PUBLIC KEY-----
	MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAzZ8nVQ0nY+cOdwTO+alX
	/yKLeqB9SIO//Z454osmjcwqF2vP+lhhOsr+pWyL9MMcrnuGzkuVW0KDmL0ej378
	jEIoK3Vzv0NLDIUesw0yBghVJk3BWIw8AXKajBJUP3X0nv/pAQjTeMQX9SoEpka5
	vrEWi0dDQWJIDWDUSHAUDHWQUDGdjewdhewuqhdqdhuwqhduweTl8rasyMinY93I
	DHEUDsnjdeuqhdNDHeuwidgh2bdjeBDEUdbedbnejHEUdhna1o2kddm1dl1ndind
	gRFZRzb/smfUMW1n/Fi3RXfWEKumvKzSG/MSVjDaAa4AlAUiSnVySa0kZK+v3oAc
	EPxzOGzl32sqQEGLjoOZC78DlJjxhwJ7g+YI8XQ92sDYB2KFPo4Bt6D20TBgtzVQ
	RpTpBmKbVGXQPMukTc5Iov0CAwEAAQ==
	-----END PUBLIC KEY-----"}' [GSENHA_API]/add/user

Response in case of success:

	HTTP 200 and a JSON:

	{"status":"success","message":"user successfully added, now you can login"}

### Login (POST /login)

Login must be done to retrieve the authentication token. This token must be sent in every request after login. 

Method: "/login"

Required JSON:

	{"username":"user","password":"password"}

Usage example:

	$curl -v -H "Content-Type: application/json" -d '{"username":"username123","password":"passwd123"}' [GSENHA_API]/login

Response in case of success:

	HTTP 200 and a JSON:

	{"token":"authentication-token"}

### Add a personal password (POST /add/password/personal)

The password will be added in a personal folder specified by the user.

Method: "/add/password/personal"

Required JSON:

	{"folder":"/Personal/UserName","name":"Senha Pessoal","passwd":"passwd123","login":"admin","url":"example.com/admin","description":"description about the password"}

* **folder** : folder where the password will be added, must be a personal folder.
* **name** : password's name
* **passwd** : the password 
* **login** : login used with the password
* **url** : the url where the password will be used
* **description** : description about the password

The fields **folder**, **name** and **passwd** are required.

Usage example:

	$curl -v -H 'Authorization: Bearer XXXXXXXX' -H "Content-Type: application/json" -d '{"folder":"/Personal/UserName","name":"PersonalPassword","passwd":"passwd123","login":"admin", "url":"example.com/admin","description":"blablabla"}' [GSENHA_API]/add/password/personal

Response in case of success:

	HTTP 200 and a JSON:

	{"status":"success","message":"password successfully added"}

### Add a shared password (POST /add/password/shared)

The password will be added in a shared folder specified by the user. 

Method: "/add/password/shared"

Required JSON:

	{"folder":"/Shared/GroupName","group":"group name","name":"Shared Password","passwd":"passwd123","login":"admin","url":"example.com/admin","description":"blablabla"}

* **folder** : folder where the password will be added, must be a shared folder.
* **name** : password's name
* **group** : group name
* **passwd** : the password 
* **login** : login used with the password
* **url** : the url where the password will be used
* **description** : description about the password

The fields **folder**, **group**, **name** and **passwd** are required. 

Usage example:

	$curl -v -H 'Authorization: Bearer XXXXXXXX' -H "Content-Type: application/json" -d '{"folder":"/Shared/GroupName","group":"group name","name":"SharedPassword","passwd":"passwd123","login":"admin", "url":"example.com/admin","description":"blablabla"}' [GSENHA_API]/add/password/shared

Response in case of success:

	HTTP 200 and a JSON:

	{"status":"success","message":"password successfully added"}

### Add a password to another user (POST /add/password/personal/external)

The password will be added, by default, in the "External" folder of the other user. The user who added the password will not have access to it. 

Method: "/add/password/personal/external"

Required JSON

	{"name":"test password","passwd":"passwd123","login":"admin","url":"example.com/admin","description":"blablabla","username":"user2"}

* **username** : the user that the password will be added
* **name** : password's name
* **passwd** : the password 
* **login** : login used with the password
* **url** : the url where the password will be used
* **description** : description about the password

The fields **name**, **passwd** and **username** are required.

Usage example:

	$curl -v -H 'Authorization: Bearer XXXXXXXX' -H "Content-Type: application/json" -d '{"username":"user2","name":"PasswordName","passwd":"passwd123","login":"admin", "url":"example.com/admin","description":"blablabla"}' [GSENHA_API]/add/password/personal/external

Response in case of success:

	HTTP 200 and a JSON:

	{"status":"success","message":"password successfully added to user2"} 

### Add a password to another group (POST /add/password/shared/external)

The password will be added, by default, in the "External" folder of the other group. The user who added the password will not have access to it. Only the members of the specified group.

Method: "/add/password/shared/external"

Required JSON

	{"name":"test passwd","passwd":"passwd123","login":"admin","url":"example.com/admin","description":"blablabla","group":"group"}

Where:

* **group** : the group the password will be added
* **name** : password's name
* **passwd** : the password
* **login** : login user with the password
* **url** : the url where the password will be used
* **description** : description about the password

The fields **name**, **passwd** and **group** are required.

Usage example:

	$curl -v -H 'Authorization: Bearer XXXXXXXX' -H "Content-Type: application/json" -d '{"group":"groupName","name":"PasswordToAnotherGroup","passwd":"passwd123","login":"admin", "url":"example.com/admin","description":"blablabla"}' [GSENHA_API]/add/password/shared/external

Response in case of success:

	HTTP 200 and a JSON:

	{"status":"success","message":"password successfully added to group"} 


### Get all passwords (GET /get/passwords)

Get all the passwords, personal and shared, that the user have authorization to access. All passwords will be encrypted, and the user have to decrypt them with his/her private key. The passwords are grouped by folder. The front-end will decrypt them for you.

Method: "/get/passwords"

Usage example:
	$curl -vvv -H 'Authorization: Bearer XXXXXXXX' [GSENHA_API]/get/passwords

Response in case of success:

	HTTP 200 and a JSON:

	{
  	"Personal Passwords": {
    	"/Personal/Leopoldo": [
      	{
        	"ID": "5", 
        	"description": "UekEyQXntQ5i++g5BFT76q38Pg8owFE9Ny/uaIiE8dyPAgHa1jy62cQ+OtIDMuvvUWRjM4wEzPVr\nbtRyHCdLrjo6ok1WYsA+5I/7pqN1MtcGltMTR3f7/nVAi/Ry933rEm+O26ik1oloAiPSWYWo0biA\nBw/haiQVap3p7Q2ESwMY5/kF7P1z+ij3GwUTMaG3BUnWnMsPZQx/6frbTc+On6XmeT0RYA06njfz\n3YQEeiC+uFrMeyIYbUh1vAV6AYVMITOzgh9Y6l7nKpBlhNTxl0zHJ9+pO1siShIjb/V3Ayq+cHpt\nP5af8dAvVNtozriIICVpwETPTh7/EPCIv2wl1RCYs8iw1VsCQI6RwPLjbMjQb4ncQ3WTIX6hkiGY\nLBZbkRySa/mDRlEx2zS0CAQLz4dMj+YycYG5Ad9VMydNW2VB5QyNXs3Z/9W6B8b43p77+nz1bBu0\nMxQhZJcUZvhMEQi9hTDT9ZNklTG0urFnbRSyS1lNMUzEv+0uilK93NblAEbirh28KKgK0kqmN1r3\nF/fCpM9y3n/rCCmYLYrywkuzsbyxkA3j0i7dgABf9ueugruMUeDxgOqV3JFPu4c6gp602n9jqWBo\nIw+G4lo2Gp7PH1OoVrY5rSaQsVHYqY+b/LSrRJmSHCdkBB255NTWu8YkTOUMpPHVDscNe9u2l6k=\n", 
        	"login": "jS6Ljwgn9jLo6buwCXq87LsVn8b0s/848YFv7drkE9VKBQF3UZ15R24nI4hO95kw/BnxgNEKqyfQ\ns6zefxnHhOtlq1MEaIKi3p4tTd5z1gQ0mXvmIATAqaKdCClr+jz7ZC7njYwtH0fw2Gyl1VqY42wY\noFLY1gQ7KOlTOnhpgjoH/i8LoHp2g6fgkEOilQdnHgS7vMY1Mo9bmAJogg7TKUeoWER5vw9qVTej\nLRCRRLYbSFF9WD+L5bDhADrad6J7CfRbMopRNlda9z85lt+Sqdm9HVFOT5/gVsguo6aqOcFQyP4X\n8/OtrfCATnesm5EFgPwEVo53rVTfmuNST8opIYGPWc7rHSKs0aESoDKV75nHa2Qsb/OSlCJ7329r\nhw+gv1jhx0ZxJRnAPWFJl7mabHkOlAFPpAkTkBISOu3x2Dv79yPCgyLDeOwOH0YhatPfPP16SOgV\nGvXh4fDQpgKd10r4eNz7qBodR4gO+6smkfkUunbkOmaL6kxjQoJUTTCoG6FidQWlB2Xnug06rjUr\nsDorRFGmKDYnojiW74ahZoOkTuSIyux7Zl+rMdF+E3rcBSrCXxhjNXdUT78+Z0PuaXwxr7H43guG\nPpPOCF7xazii47/2B8r55UfP/9RlZpQSuCz2IflaY/rwmZgk62J5bmUWnpLaIu1cZhJtVuep/1o=\n", 
        	"name": "Senha Teste 1", 
        	"password": "LOT+Ctu8UbTIfFWwzMX/kdBcja2VfGJDwKzJ4u0v/uiooMKOwNKbJ0t+tHLIkQWs6+ZV5QAcoBvz\nl0FAqWRwRKqmVvaHZptIE5WE3WQyP78NvpjinNK5LZ6MMsX5iBqsf3aN/qvWZDPXCYM01Ho0NRgJ\nZQRvPX32RNV1PHd1+nD38RG+nqT7uvkmcTUibHuepkak2atfMhn4zOlrB9W7qbzvjxaMnVws7GRU\nKFJ3BK/2g/yhr7y+/0OuhYQOF/WtW6KDH7eeH4AfgsJ9GMUxy3AnTmd56wAcFnnfY6iBYFd+XfVK\nlf93hKuze2jWp/rjY5sqiG8eLQNCndGUFHyMVzjafTkK5nnKyH8fiFR5qP66V16tDnVnl0L0Uhc4\njMRj4rwTnjeHvdOLeAmmJqw2wwUabFdvma0WZimWwaSa1GgF7Bsn1qAkTqP+d2YA2kzfAjj4aJ14\nTQ/ZoA1joSN39VzTKmFOysItndh7/RpIh0iVv9msiIaXnzxzLUJdk7ikiXGHT1tmfgs8AoYpiX59\ndWHuUEn2lQb/eKMqo8IbidVE8csnf6O9IdMF+JvW0qjAWhSh51Qd5LMUk8D5jn6oMuLEYKeZQosF\njWVT+ejHCRTL5++mqgoaidS7AcP4ksZqpjLF6UKmHSEJf3xz1ty3yveOx+9LBXxGOjnJLAkIqK8=\n", 
       		"url": "Kj9qgSpaWHuRidaZfXlfLJPC1C3J+Mne8JmQbesBfIaJuTsEQoTLSR4wdvdE05mqPLIhLs3kpSya\nv3TGNt/0YS8l/+0ncVyoMmKufllIT4TomvIC018D4jzRsUcZU5igNV5gCYXHU/3CKH5+lsHBUsZE\no5hFWhh2zIZDTOiJ6pdjMncgy156M+JKsJwDYo7crB647vCaR8RxiW5faOBx3wghRqra5KOlyzW8\nt78stDILg87LacHddQ2fLtHyPtkJvWUct3Gm0E3KqAFaIviBodVgQk7bU6+UDJLV6/Wj+Q8KqKhZ\nARcnXM8LmlqbUyYfcxoHmQnvaAl9qnC1tCAhsIEUWOM9+201V6/nwbaSgBuhSHe+GBwVS7OxjmkW\nR4jUj1wgnALTgGCgA96HZBg9D/5YeL6px76VbXsY5Wp3PyEBlFgN09ZuedxqzT8r+WcTKOlCBbFO\nwZGEY114lpklHSWWWSjl8AuLVhWkgqGVIUSB0B4PIuUfkqMNcyLoPjA/nO3PJ1q0y7gpI//Vhnht\nPZnye0u464rVI23KnB/5FKFaccGziFqSbNspa//vwV4Mcp4wujod+/ye8TcxsbKVHbHf7HTDcyi3\n8E6lqRvvxVmy4YRBQiYk3ujSseNv+GgcJISBKaXj0MgkfFEdJaRwZHyCc2uolQZyphKVIajybTo=\n"
      	}
    ]
    }, 
    "Shared Passwords": { 
        "/Shared/group1": [
        {
        	"ID": "6", 
        	"description": "UekEyQXntQ5i++g5BFT76q38Pg8owFE9Ny/uaIiE8dyPAgHa1jy62cQ+OtIDMuvvUWRjM4wEzPVr\nbtRyHCdLrjo6ok1WYsA+5I/7pqN1MtcGltMTR3f7/nVAi/Ry933rEm+O26ik1oloAiPSWYWo0biA\nBw/haiQVap3p7Q2ESwMY5/kF7P1z+ij3GwUTMaG3BUnWnMsPZQx/6frbTc+On6XmeT0RYA06njfz\n3YQEeiC+uFrMeyIYbUh1vAV6AYVMITOzgh9Y6l7nKpBlhNTxl0zHJ9+pO1siShIjb/V3Ayq+cHpt\nP5af8dAvVNtozriIICVpwETPTh7/EPCIv2wl1RCYs8iw1VsCQI6RwPLjbMjQb4ncQ3WTIX6hkiGY\nLBZbkRySa/mDRlEx2zS0CAQLz4dMj+YycYG5Ad9VMydNW2VB5QyNXs3Z/9W6B8b43p77+nz1bBu0\nMxQhZJcUZvhMEQi9hTDT9ZNklTG0urFnbRSyS1lNMUzEv+0uilK93NblAEbirh28KKgK0kqmN1r3\nF/fCpM9y3n/rCCmYLYrywkuzsbyxkA3j0i7dgABf9ueugruMUeDxgOqV3JFPu4c6gp602n9jqWBo\nIw+G4lo2Gp7PH1OoVrY5rSaQsVHYqY+b/LSrRJmSHCdkBB255NTWu8YkTOUMpPHVDscNe9u2l6k=\n", 
        	"login": "jS6Ljwgn9jLo6buwCXq87LsVn8b0s/848YFv7drkE9VKBQF3UZ15R24nI4hO95kw/BnxgNEKqyfQ\ns6zefxnHhOtlq1MEaIKi3p4tTd5z1gQ0mXvmIATAqaKdCClr+jz7ZC7njYwtH0fw2Gyl1VqY42wY\noFLY1gQ7KOlTOnhpgjoH/i8LoHp2g6fgkEOilQdnHgS7vMY1Mo9bmAJogg7TKUeoWER5vw9qVTej\nLRCRRLYbSFF9WD+L5bDhADrad6J7CfRbMopRNlda9z85lt+Sqdm9HVFOT5/gVsguo6aqOcFQyP4X\n8/OtrfCATnesm5EFgPwEVo53rVTfmuNST8opIYGPWc7rHSKs0aESoDKV75nHa2Qsb/OSlCJ7329r\nhw+gv1jhx0ZxJRnAPWFJl7mabHkOlAFPpAkTkBISOu3x2Dv79yPCgyLDeOwOH0YhatPfPP16SOgV\nGvXh4fDQpgKd10r4eNz7qBodR4gO+6smkfkUunbkOmaL6kxjQoJUTTCoG6FidQWlB2Xnug06rjUr\nsDorRFGmKDYnojiW74ahZoOkTuSIyux7Zl+rMdF+E3rcBSrCXxhjNXdUT78+Z0PuaXwxr7H43guG\nPpPOCF7xazii47/2B8r55UfP/9RlZpQSuCz2IflaY/rwmZgk62J5bmUWnpLaIu1cZhJtVuep/1o=\n", 
        	"name": "Senha Teste 2", 
        	"password": "LOT+Ctu8UbTIfFWwzMX/kdBcja2VfGJDwKzJ4u0v/uiooMKOwNKbJ0t+tHLIkQWs6+ZV5QAcoBvz\nl0FAqWRwRKqmVvaHZptIE5WE3WQyP78NvpjinNK5LZ6MMsX5iBqsf3aN/qvWZDPXCYM01Ho0NRgJ\nZQRvPX32RNV1PHd1+nD38RG+nqT7uvkmcTUibHuepkak2atfMhn4zOlrB9W7qbzvjxaMnVws7GRU\nKFJ3BK/2g/yhr7y+/0OuhYQOF/WtW6KDH7eeH4AfgsJ9GMUxy3AnTmd56wAcFnnfY6iBYFd+XfVK\nlf93hKuze2jWp/rjY5sqiG8eLQNCndGUFHyMVzjafTkK5nnKyH8fiFR5qP66V16tDnVnl0L0Uhc4\njMRj4rwTnjeHvdOLeAmmJqw2wwUabFdvma0WZimWwaSa1GgF7Bsn1qAkTqP+d2YA2kzfAjj4aJ14\nTQ/ZoA1joSN39VzTKmFOysItndh7/RpIh0iVv9msiIaXnzxzLUJdk7ikiXGHT1tmfgs8AoYpiX59\ndWHuUEn2lQb/eKMqo8IbidVE8csnf6O9IdMF+JvW0qjAWhSh51Qd5LMUk8D5jn6oMuLEYKeZQosF\njWVT+ejHCRTL5++mqgoaidS7AcP4ksZqpjLF6UKmHSEJf3xz1ty3yveOx+9LBXxGOjnJLAkIqK8=\n", 
       		"url": "Kj9qgSpaWHuRidaZfXlfLJPC1C3J+Mne8JmQbesBfIaJuTsEQoTLSR4wdvdE05mqPLIhLs3kpSya\nv3TGNt/0YS8l/+0ncVyoMmKufllIT4TomvIC018D4jzRsUcZU5igNV5gCYXHU/3CKH5+lsHBUsZE\no5hFWhh2zIZDTOiJ6pdjMncgy156M+JKsJwDYo7crB647vCaR8RxiW5faOBx3wghRqra5KOlyzW8\nt78stDILg87LacHddQ2fLtHyPtkJvWUct3Gm0E3KqAFaIviBodVgQk7bU6+UDJLV6/Wj+Q8KqKhZ\nARcnXM8LmlqbUyYfcxoHmQnvaAl9qnC1tCAhsIEUWOM9+201V6/nwbaSgBuhSHe+GBwVS7OxjmkW\nR4jUj1wgnALTgGCgA96HZBg9D/5YeL6px76VbXsY5Wp3PyEBlFgN09ZuedxqzT8r+WcTKOlCBbFO\nwZGEY114lpklHSWWWSjl8AuLVhWkgqGVIUSB0B4PIuUfkqMNcyLoPjA/nO3PJ1q0y7gpI//Vhnht\nPZnye0u464rVI23KnB/5FKFaccGziFqSbNspa//vwV4Mcp4wujod+/ye8TcxsbKVHbHf7HTDcyi3\n8E6lqRvvxVmy4YRBQiYk3ujSseNv+GgcJISBKaXj0MgkfFEdJaRwZHyCc2uolQZyphKVIajybTo=\n"
        }, 
        {
        	"ID": "7", 
        	"description": "UekEyQXntQ5i++g5BFT76q38Pg8owFE9Ny/uaIiE8dyPAgHa1jy62cQ+OtIDMuvvUWRjM4wEzPVr\nbtRyHCdLrjo6ok1WYsA+5I/7pqN1MtcGltMTR3f7/nVAi/Ry933rEm+O26ik1oloAiPSWYWo0biA\nBw/haiQVap3p7Q2ESwMY5/kF7P1z+ij3GwUTMaG3BUnWnMsPZQx/6frbTc+On6XmeT0RYA06njfz\n3YQEeiC+uFrMeyIYbUh1vAV6AYVMITOzgh9Y6l7nKpBlhNTxl0zHJ9+pO1siShIjb/V3Ayq+cHpt\nP5af8dAvVNtozriIICVpwETPTh7/EPCIv2wl1RCYs8iw1VsCQI6RwPLjbMjQb4ncQ3WTIX6hkiGY\nLBZbkRySa/mDRlEx2zS0CAQLz4dMj+YycYG5Ad9VMydNW2VB5QyNXs3Z/9W6B8b43p77+nz1bBu0\nMxQhZJcUZvhMEQi9hTDT9ZNklTG0urFnbRSyS1lNMUzEv+0uilK93NblAEbirh28KKgK0kqmN1r3\nF/fCpM9y3n/rCCmYLYrywkuzsbyxkA3j0i7dgABf9ueugruMUeDxgOqV3JFPu4c6gp602n9jqWBo\nIw+G4lo2Gp7PH1OoVrY5rSaQsVHYqY+b/LSrRJmSHCdkBB255NTWu8YkTOUMpPHVDscNe9u2l6k=\n", 
        	"login": "jS6Ljwgn9jLo6buwCXq87LsVn8b0s/848YFv7drkE9VKBQF3UZ15R24nI4hO95kw/BnxgNEKqyfQ\ns6zefxnHhOtlq1MEaIKi3p4tTd5z1gQ0mXvmIATAqaKdCClr+jz7ZC7njYwtH0fw2Gyl1VqY42wY\noFLY1gQ7KOlTOnhpgjoH/i8LoHp2g6fgkEOilQdnHgS7vMY1Mo9bmAJogg7TKUeoWER5vw9qVTej\nLRCRRLYbSFF9WD+L5bDhADrad6J7CfRbMopRNlda9z85lt+Sqdm9HVFOT5/gVsguo6aqOcFQyP4X\n8/OtrfCATnesm5EFgPwEVo53rVTfmuNST8opIYGPWc7rHSKs0aESoDKV75nHa2Qsb/OSlCJ7329r\nhw+gv1jhx0ZxJRnAPWFJl7mabHkOlAFPpAkTkBISOu3x2Dv79yPCgyLDeOwOH0YhatPfPP16SOgV\nGvXh4fDQpgKd10r4eNz7qBodR4gO+6smkfkUunbkOmaL6kxjQoJUTTCoG6FidQWlB2Xnug06rjUr\nsDorRFGmKDYnojiW74ahZoOkTuSIyux7Zl+rMdF+E3rcBSrCXxhjNXdUT78+Z0PuaXwxr7H43guG\nPpPOCF7xazii47/2B8r55UfP/9RlZpQSuCz2IflaY/rwmZgk62J5bmUWnpLaIu1cZhJtVuep/1o=\n", 
        	"name": "Senha Teste 3", 
        	"password": "LOT+Ctu8UbTIfFWwzMX/kdBcja2VfGJDwKzJ4u0v/uiooMKOwNKbJ0t+tHLIkQWs6+ZV5QAcoBvz\nl0FAqWRwRKqmVvaHZptIE5WE3WQyP78NvpjinNK5LZ6MMsX5iBqsf3aN/qvWZDPXCYM01Ho0NRgJ\nZQRvPX32RNV1PHd1+nD38RG+nqT7uvkmcTUibHuepkak2atfMhn4zOlrB9W7qbzvjxaMnVws7GRU\nKFJ3BK/2g/yhr7y+/0OuhYQOF/WtW6KDH7eeH4AfgsJ9GMUxy3AnTmd56wAcFnnfY6iBYFd+XfVK\nlf93hKuze2jWp/rjY5sqiG8eLQNCndGUFHyMVzjafTkK5nnKyH8fiFR5qP66V16tDnVnl0L0Uhc4\njMRj4rwTnjeHvdOLeAmmJqw2wwUabFdvma0WZimWwaSa1GgF7Bsn1qAkTqP+d2YA2kzfAjj4aJ14\nTQ/ZoA1joSN39VzTKmFOysItndh7/RpIh0iVv9msiIaXnzxzLUJdk7ikiXGHT1tmfgs8AoYpiX59\ndWHuUEn2lQb/eKMqo8IbidVE8csnf6O9IdMF+JvW0qjAWhSh51Qd5LMUk8D5jn6oMuLEYKeZQosF\njWVT+ejHCRTL5++mqgoaidS7AcP4ksZqpjLF6UKmHSEJf3xz1ty3yveOx+9LBXxGOjnJLAkIqK8=\n", 
       		"url": "Kj9qgSpaWHuRidaZfXlfLJPC1C3J+Mne8JmQbesBfIaJuTsEQoTLSR4wdvdE05mqPLIhLs3kpSya\nv3TGNt/0YS8l/+0ncVyoMmKufllIT4TomvIC018D4jzRsUcZU5igNV5gCYXHU/3CKH5+lsHBUsZE\no5hFWhh2zIZDTOiJ6pdjMncgy156M+JKsJwDYo7crB647vCaR8RxiW5faOBx3wghRqra5KOlyzW8\nt78stDILg87LacHddQ2fLtHyPtkJvWUct3Gm0E3KqAFaIviBodVgQk7bU6+UDJLV6/Wj+Q8KqKhZ\nARcnXM8LmlqbUyYfcxoHmQnvaAl9qnC1tCAhsIEUWOM9+201V6/nwbaSgBuhSHe+GBwVS7OxjmkW\nR4jUj1wgnALTgGCgA96HZBg9D/5YeL6px76VbXsY5Wp3PyEBlFgN09ZuedxqzT8r+WcTKOlCBbFO\nwZGEY114lpklHSWWWSjl8AuLVhWkgqGVIUSB0B4PIuUfkqMNcyLoPjA/nO3PJ1q0y7gpI//Vhnht\nPZnye0u464rVI23KnB/5FKFaccGziFqSbNspa//vwV4Mcp4wujod+/ye8TcxsbKVHbHf7HTDcyi3\n8E6lqRvvxVmy4YRBQiYk3ujSseNv+GgcJISBKaXj0MgkfFEdJaRwZHyCc2uolQZyphKVIajybTo=\n"
        }
    ]
    }

### Get all groups (GET /get/groups)

Useful when adding a password to a group you are not member of. 

Method: "/get/groups"

Usage example:
	$curl -v -H 'Authorization: Bearer XXXXXXXX' [GSENHA_API]/get/groups

Response in case of success:

	HTTP 200 and a JSON:

	{
 	 "Groups": [
    	"group1", 
    	"group2", 
    	"group3", 
    	"group4", 
    	"group5"
  		]
	}


### Get your groups (GET /get/mygroups)

Get the groups you are member of.

Method: "/get/mygroups"

Usage example:
	$curl -vvv -H 'Authorization: Bearer XXXXXXXX' [GSENHA_API]/get/mygroups

Response in case of success:

	HTTP 200 and a JSON:

	{
 	 "Groups": [ 
    	"group1"
  		]
	}

### Get your folders (GET /get/folders)

Get your folders, and the shared folders you have access.

Method: "/get/folders"

Usage example:
	$curl -vvv -H 'Authorization: Bearer XXXXXXXX' [GSENHA_API]/get/folders

Response in case of success:

	HTTP 200 and a JSON:

	{
  	"Group Folders": [
    		"/Shared/group1", 
    		"/Shared/group2"
  		], 
  	"Personal Folders": [
    		"/Personal/Leopoldo"
  		]
	}

### Get your directory tree (GET /get/tree)

Get all your folders in a tree architecture.

Method: "/get/tree"

Usage example:
	$curl -v -H 'Authorization: Bearer XXXXXXXX' [GSENHA_API]/get/tree

Response in case of success:

	HTTP 200 and a JSON:

	{
	  "Folders": [
	    {
	      "Personal Folders": [
	        {
	          "name": "/Personal/User",        
	          "children": [
	            {
	              "name": "/Personal/User/External",
	              "name": "/Personal/User/Teste"
	            }
	          ]
	        }
	      ]
	    }, 
	    {
	      "Group Folders": [ 
	          {
				"name": "/Shared/group1",
	            "children": [
	              {
	                "name": "/Shared/group1/External"
	              }
	            ]
	          }
	        ]
		}	


### Unlock shared passwords to a new user - part 1 (POST /unlock)

Unlock a new user to see the previously added shared passwords. It is necessary that a user who already have access to the passwords perform this action. It is made in two parts.

Method: "/unlock"

Required JSON:

	{"group":"grupName","usertounlock":"user to be unlocked"}

* **group**: group of the new user. The user performing this action must be a member of the same group. 
* **usertounlock**: the user that will be unlocked

All fields are required.

Usage example:

	$curl -v -H 'Authorization: Bearer XXXXXXXX' -H "Content-Type: application/json" -d '{"group":"groupName","usertounlock":"user2"}' [GSENHA_API]/unlock

Response in case of success:

	{"status":"success","passwords":[{"idGrupo":"123","idPastas":"1234","idCompartilhado":"111","passwd":"encrypted passwd base64 encoded","name":"passwd123","login":"encrypted login base64 encoded","url":"encrypted url base64 encoded","description":"encrypted description base64 encoded"},{"idGrupo":"123","idPastas":"1234","idCompartilhado":"111","passwd":"encrypted passwd base64 encoded","name":"passwd123","login":"encrypted login base64 encoded","url":"encrypted url base64 encoded","description":"encrypted description base64 encoded"}],"pubkey":"-----BEGIN PUBLIC KEY----- ... -----END PUBLIC KEY-----","token":"token"}

All passwords are retrieved encrypted, and the user who is performing the request should decrypt them, and encrypt again with the public key received. All metadata must not be modified. An integrity teste will be made on server side, if it fails the request will not work. 

After the decryption and re-encryption, the user who made the first request will have to make another one, listed below, to finally unlock the user. 

### Unlock shared passwords to a new user - part 2 (POST /unlocking)

Method: "/unlocking"

Required JSON:

	{"group":"grup","usertounlock":"user2","passwords":[],"token":"token"}

The token must be the same received on the previously request, and the passwords field must be the passwords encrypted with the server public key.

Usage example:

	$curl -v -H 'Authorization: Bearer XXXXXXXX' -H "Content-Type: application/json" -d '{"token":"token from part 1","usertounlock":"user2","passwords":[{},{},{}]}' [GSENHA_API]/unlock

Response in case of success:

	{"status":"success","message":"Passwords successfully unlocked"}

### Add a folder (POST /add/folder)

Add a subfolder. You can not add a root folder. 

Method: "/add/folder"

Required JSON:

	{"path":"pathFolder","name":"folderName"}

Where:

* **path**: it is the path where the folder will be added
* **name**: folder's name

All fields are required.

OBS: To know all available paths use the method /get/folders . 

Usage example:

	$curl -v -H 'Authorization: Bearer XXXXXXXX' -H "Content-Type: application/json" -d '{"path":"/Personal/User","name":"FolderName"}' [GSENHA_API]/add/folder

Response in case of success:

	{"status":"success","message":"Folder successfully added"}

### Delete a folder (POST /delete/folder)

Required JSON:

	{"folder":"FolderName"}

OBS: It is only possible to delete empty folders.

Usage example:

	$curl -v -H 'Authorization: Bearer XXXXXXXX' -H 'Content-Type: application/json' -d '{"folder":"FolderName"}' [GSENHA_API]/add/folder

Response in case of success:

	{"status":"success","message":"Folder successfully deleted"}	

### Update a password (POST /update/password) 

Method: "/update/password"

Required JSON:

	{"id":"1","passwd":"passswd123","url":"example.com/admin","login":"admin","name":"PasswdName","description":"blablabla"}

Obs: The "id" field is required, the others will be updated if informed.

Usage example:

	$curl -vvv -H 'Authorization: Bearer XXXXXXXX' -H "Content-Type: application/json" -d '{"id":"1","passwd":"passd456","url":"example.com/admin","login":"root","name":"other Name","description":"blablabla2"}' [GSENHA_API]/update/password

Response in case of success:

	{"status":"success","message":"Password successfully updated"}

### Delete a password (DELETE /delete/password/<int:idPassword>)

Delete a password, in case of shared passwords it will be deleted for all members. 

Usage example:

	$curl -vvv -H 'Authorization: Bearer XXXXXXXX' -X "DELETE" [GSENHA_API]/delete/password/123

Response in case of success:

	{"status":"success","message":"Password successfully deleted"}

### Get a specific password (POST /search/password)

Get a specific password given its name and folder. 

Method: "/search/password"

Required JSON:

	{"folder":"/Personal/User","name":"FolderName"}

Usage example:

	$curl -vvv -H 'Authorization: Bearer XXXXXXXX' -H "Content-Type: application/json" -d '{"folder":"/Personal/User","name":"Passwd Name"}' [GSENHA_API]/search/password

Response in case of success:

	{"status":"success","password":{"name":"nome","passwd":"passwd123","url":"url","login":"login","description":"description"}}
