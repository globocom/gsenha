GSENHA API
==========

GSenha-API is a password manager, but not an usual one. Its architecture was designed to avoid information leakage in the case of a compromise. It is possible to store a password and share it among a group of users in a secure way, and also store a personal password, just for yourself. Storing a personal password is just like using another well-known password manager like KeePass, PasswordSafe, Password Gorilla and others. The goal in GSenha is to be able to store a password and allow other users to have access to it in a secure way, without backdoors and no shared secret keys. This is done with asymmetric cryptography (private and public keys).

GSenha-API works as a REST API with JWT. There is a front-end (GSenha), but anyone can write a custom one or use it as a command line tool. 

There is one dependency, you must have a LDAP base. GSenha does not perform user management, it uses the information provided in the LDAP base. Authentication and authorization are all handled by the LDAP. A new user must add herself/himself into the system informing his/her LDAP's credentials and a RSA public key. Gsenha will perform a query on the LDAP server and, once authentication is granted, all user information will be retrieved, like given name, surname, email, groups and it will be stored in a database with the public key. After that, the user will perform a login using his/her LDAP's credentials. In all requests of the API it will be performed a query into LDAP to see if there is any inconsistency with the user and his/her groups. The GSenha-API's database group table will mirror LDAP's base. This is how authorization is handled. 

Presentations
-------------

[Slides for presentation at the Nic.br Security Working Group (GTS25) - Only in Portuguese](ftp://ftp.registro.br/pub/gts/gts25/07-GerenciamentoSenhas.pdf)
[Video for presentation at the Nic.br Security Working Group (GTS25) - Only in Portuguese](https://www.youtube.com/watch?v=WNtcEJK80TU)

Private key fallback
----------------------

The system is not able to retrieve your private key in case of loss. It is user's obligation to keep his/her private key safe. **DO NOT LOSE YOUR PRIVATE KEY!**

Want to know more?
------------------

Take a look at our excellent [documentation](https://github.com/globocom/gsenha-api/wiki)!