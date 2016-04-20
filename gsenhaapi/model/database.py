# -*- coding: utf-8 -*-
import MySQLdb

class DataBase:

	def __init__ (self, host, user, password, database):
			self.host = host
			self.user = user
			self.password = password
			self.database = database
			self.db = MySQLdb.connect(host=self.host,user=self.user,passwd=self.password,db=self.database)	
			self.c = self.db.cursor()

	def connect(self):
		self.db = MySQLdb.connect(host=self.host,user=self.user,passwd=self.password,db=self.database)
		self.c = self.db.cursor()

	def healthcheck(self):
		try:
			self.c.execute("SELECT VERSION()")
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT VERSION()")
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
				return 0
			except IndexError:
				message = "MySQL Error: %s" % str(e)
				return 0
		return 1

	def search_user_db(self,username):
		try:
			self.c.execute("SELECT idUsuario FROM Usuarios WHERE username = %s;",[username])
			idUsuario = self.c.fetchone()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT idUsuario FROM Usuarios WHERE username = %s;",[username])
			idUsuario = self.c.fetchone()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
				return message , 0
			except IndexError:
				message = "MySQL Error: %s" % str(e)
				return message , 0
		return idUsuario , 1

	def get_user_info_db(self,username):
		try:
			self.c.execute("SELECT Email,NomeUsuario FROM Usuarios WHERE username = %s;",[username])
			info = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT Email,NomeUsuario FROM Usuarios WHERE username = %s;",[username])
			info = self.c.fetchall()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return info , 1

	def get_user_name_db(self,idUsuario):
		try:
			self.c.execute("SELECT NomeUsuario FROM Usuarios WHERE idUsuario = %s;",[idUsuario])
			name = self.c.fetchone()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT NomeUsuario FROM Usuarios WHERE idUsuario = %s;",[idUsuario])
			name = self.c.fetchone()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return name , 1

	#pega o id do grupo de acordo com o nome do grupo
	def search_group_db(self,NomeGrupo):
		try:
			self.c.execute("SELECT idGrupo FROM Grupos WHERE NomeGrupo = %s;",[NomeGrupo])
			idGrupo = self.c.fetchone()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT idGrupo FROM Grupos WHERE NomeGrupo = %s;",[NomeGrupo])
			idGrupo = self.c.fetchone()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return idGrupo , 1 

	#adiciona o usuario
	def add_user_db(self,NomeUsuario,Email,username,pubkey):
		try:
			self.c.execute("INSERT INTO Usuarios (NomeUsuario,Email,username,PublicKey) VALUES (%s,%s,%s,%s);",(NomeUsuario,Email,username,pubkey))
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("INSERT INTO Usuarios (NomeUsuario,Email,username,PublicKey) VALUES (%s,%s,%s,%s);",(NomeUsuario,Email,username,pubkey))
			self.db.commit()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK" ,  1

	#adiciona o grupo
	def add_group_db(self,NomeGrupo):
		try:
			self.c.execute("INSERT INTO Grupos (NomeGrupo) VALUES (%s);",[NomeGrupo])
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("INSERT INTO Grupos (NomeGrupo) VALUES (%s);",[NomeGrupo])
			self.db.commit()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK" , 1

	#adiciona a relacao usuario-grupo
	def add_user_group_db(self,idUsuario,idGrupo):
		try:
			self.c.execute("INSERT INTO Usuario_Grupo (Usuarios_idUsuario,Grupos_idGrupo) VALUES (%s,%s);",(idUsuario,idGrupo))
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("INSERT INTO Usuario_Grupo (Usuarios_idUsuario,Grupos_idGrupo) VALUES (%s,%s);",(idUsuario,idGrupo))
			self.db.commit()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK", 1

	#adiciona a pasta pessoal do usuario
	def add_userfolder_db(self,NomePasta,caminho,idUsuario):
		try:
			self.c.execute("LOCK TABLES Pastas WRITE, Usuarios WRITE;")
			self.c.execute("SELECT @myLeft:= lft FROM Pastas WHERE NomePasta = %s;",[caminho])
			self.c.execute("UPDATE Pastas SET rgt = (rgt + 2) WHERE rgt > @myLeft;")
			self.c.execute("UPDATE Pastas SET lft = (lft + 2) WHERE lft > @myLeft;")
			query = ("INSERT INTO Pastas (NomePasta,lft,rgt,Grupos_idGrupo,Usuarios_idUsuario) VALUES"
				"(%s,@myLeft +1,@myLeft +2,NULL,%s);")
			data = (NomePasta,idUsuario)
			self.c.execute(query,data)
			self.c.execute("UNLOCK TABLES;")
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("LOCK TABLES Pastas WRITE, Usuarios WRITE;")
			self.c.execute("SELECT @myLeft:= lft FROM Pastas WHERE NomePasta = %s;",[caminho])
			self.c.execute("UPDATE Pastas SET rgt = (rgt + 2) WHERE rgt > @myLeft;")
			self.c.execute("UPDATE Pastas SET lft = (lft + 2) WHERE lft > @myLeft;")
			query = ("INSERT INTO Pastas (NomePasta,lft,rgt,Grupos_idGrupo,Usuarios_idUsuario) VALUES"
				"(%s,@myLeft +1,@myLeft +2,NULL,%s);")
			data = (NomePasta,idUsuario)
			self.c.execute(query,data)
			self.c.execute("UNLOCK TABLES;")
			self.db.commit()
		except MySQLdb.Error,e:
			self.db.rollback()
			self.c.execute("UNLOCK TABLES;")
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK" , 1

	def add_groupfolder_db(self,NomePasta,caminho,idGrupo):
		try:
			self.c.execute("LOCK TABLES Pastas WRITE, Grupos WRITE;")
			self.c.execute("SELECT @myLeft:= lft FROM Pastas WHERE NomePasta = %s;",[caminho])
			self.c.execute("UPDATE Pastas SET rgt = (rgt + 2) WHERE rgt > @myLeft;")
			self.c.execute("UPDATE Pastas SET lft = (lft + 2) WHERE lft > @myLeft;")
			query = ("INSERT INTO Pastas (NomePasta,lft,rgt,Grupos_idGrupo,Usuarios_idUsuario) VALUES"
				"(%s,@myLeft +1,@myLeft +2,%s,NULL);")
			data = (NomePasta,idGrupo)
			self.c.execute(query,data)
			self.c.execute("UNLOCK TABLES;")
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("LOCK TABLES Pastas WRITE, Grupos WRITE;")
			self.c.execute("SELECT @myLeft:= lft FROM Pastas WHERE NomePasta = %s;",[caminho])
			self.c.execute("UPDATE Pastas SET rgt = (rgt + 2) WHERE rgt > @myLeft;")
			self.c.execute("UPDATE Pastas SET lft = (lft + 2) WHERE lft > @myLeft;")
			query = ("INSERT INTO Pastas (NomePasta,lft,rgt,Grupos_idGrupo,Usuarios_idUsuario) VALUES"
				"(%s,@myLeft +1,@myLeft +2,%s,NULL);")
			data = (NomePasta,idGrupo)
			self.c.execute(query,data)
			self.c.execute("UNLOCK TABLES;")
			self.db.commit()
		except MySQLdb.Error,e:
			self.db.rollback()
			self.c.execute("UNLOCK TABLES;")
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK" , 1

	def delete_groupfolder_db(self,NomePasta,idGrupo):
		try:
			self.c.execute("LOCK TABLE Pastas WRITE, Grupos WRITE;")
			self.c.execute("SELECT @myLeft := lft, @myRight := rgt, @myWidth := rgt - lft + 1 FROM Pastas WHERE NomePasta = %s AND Grupos_idGrupo = %s;",(NomePasta,idGrupo))
			self.c.execute("DELETE FROM Pastas WHERE lft BETWEEN @myLeft AND @myRight;")
			self.c.execute("UPDATE Pastas SET rgt = rgt - @myWidth WHERE rgt > @myRight;")
			self.c.execute("UPDATE Pastas SET lft = lft - @myWidth WHERE lft > @myRight;")
			self.c.execute("UNLOCK TABLES;")
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.c.connect()
			self.c.execute("LOCK TABLE Pastas WRITE, Grupos WRITE;")
			self.c.execute("SELECT @myLeft := lft, @myRight := rgt, @myWidth := rgt - lft + 1 FROM Pastas WHERE NomePasta = %s AND Grupos_idGrupo = %s;",(NomePasta,idGrupo))
			self.c.execute("DELETE FROM Pastas WHERE lft BETWEEN @myLeft AND @myRight;")
			self.c.execute("UPDATE Pastas SET rgt = rgt - @myWidth WHERE rgt > @myRight;")
			self.c.execute("UPDATE Pastas SET lft = lft - @myWidth WHERE lft > @myRight;")
			self.c.execute("UNLOCK TABLES;")
			self.db.commit()
		except MySQLdb.Error,e:
			self.db.rollback()
			self.c.execute("UNLOCK TABLES;")
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK" , 1			

	def delete_userfolder_db(self,NomePasta,idUsuario):
		try:
			self.c.execute("LOCK TABLE Pastas WRITE, Grupos WRITE;")
			self.c.execute("SELECT @myLeft := lft, @myRight := rgt, @myWidth := rgt - lft + 1 FROM Pastas WHERE NomePasta = %s AND Usuarios_idUsuario = %s;",(NomePasta,idUsuario))
			self.c.execute("DELETE FROM Pastas WHERE lft BETWEEN @myLeft AND @myRight;")
			self.c.execute("UPDATE Pastas SET rgt = rgt - @myWidth WHERE rgt > @myRight;")
			self.c.execute("UPDATE Pastas SET lft = lft - @myWidth WHERE lft > @myRight;")
			self.c.execute("UNLOCK TABLES;")
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.c.connect()
			self.c.execute("LOCK TABLE Pastas WRITE, Grupos WRITE;")
			self.c.execute("SELECT @myLeft := lft, @myRight := rgt, @myWidth := rgt - lft + 1 FROM Pastas WHERE NomePasta = %s AND Usuarios_idUsuario = %s;",(NomePasta,idUsuario))
			self.c.execute("DELETE FROM Pastas WHERE lft BETWEEN @myLeft AND @myRight;")
			self.c.execute("UPDATE Pastas SET rgt = rgt - @myWidth WHERE rgt > @myRight;")
			self.c.execute("UPDATE Pastas SET lft = lft - @myWidth WHERE lft > @myRight;")
			self.c.execute("UNLOCK TABLES;")
			self.db.commit()
		except MySQLdb.Error,e:
			self.db.rollback()
			self.c.execute("UNLOCK TABLES;")
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK" , 1

	def get_userfolder(self,idUsuario):
		try:
			self.c.execute("SELECT NomePasta,idPasta FROM Pastas WHERE  Usuarios_idUsuario = %s;",[idUsuario])
			folders = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT NomePasta FROM Pastas WHERE  Usuarios_idUsuario = %s;",[idUsuario])
			folders = self.c.fetchall()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return folders, 1

	def get_groupfolder(self,NomeGrupo):
		try:
			self.c.execute("SELECT NomePasta,idPasta FROM Pastas WHERE Grupos_idGrupo = (SELECT idGrupo FROM Grupos WHERE NomeGrupo = %s)",[NomeGrupo])
			folders = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT NomePasta FROM Pastas WHERE Grupos_idGrupo = (SELECT idGrupo FROM Grupos WHERE NomeGrupo = %s)",[NomeGrupo])
			folders = self.c.fetchall()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return folders, 1

	#adiciona uma chave pessoal
	def add_personalpassword_db(self,NomeGrupo,username,NomePasta,senha,nome,login,url,descricao):
		query = ("INSERT INTO Passwords (Usuario_idUsuario,Grupo_idGrupo,Pastas_idPastas,idCompartilhado,senha,url,login,descricao,nome)"
				"VALUES ((SELECT idUsuario FROM Usuarios WHERE username=%s),"
				"(SELECT idGrupo FROM Grupos WHERE NomeGrupo = %s),"
				"(SELECT idPasta FROM Pastas WHERE NomePasta = %s),"
				"0,%s,%s,%s,%s,%s);")
		data = (username,NomeGrupo,NomePasta,senha,url,login,descricao,nome)
		try:
			self.c.execute(query,data)
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute(query,data)
			self.db.commit()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK",1

	def add_sharedpassword_db(self,NomeGrupo,idUsuario,NomePasta,idCompartilhado,senha,nome,login,url,descricao):
		query = ("INSERT INTO Passwords (Usuario_idUsuario,Grupo_idGrupo,Pastas_idPastas,idCompartilhado,senha,url,login,descricao,nome)" 
				"VALUES (%s," 
				"(SELECT idGrupo FROM Grupos WHERE NomeGrupo = %s),"
				"(SELECT idPasta FROM Pastas WHERE NomePasta = %s),"
				"%s,%s,%s,%s,%s,%s);")
		data = (idUsuario,NomeGrupo,NomePasta,idCompartilhado,senha,url,login,descricao,nome)
		try:
			self.c.execute(query,data)
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute(query,data)
			self.db.commit()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK",1

	def add_sharedpassword_special_db(self,NomeGrupo,idUsuario,NomePasta,senha,nome,login,url,descricao):
		query = ("UPDATE Passwords SET senha = %s , descricao = %s , url = %s , login = %s  WHERE nome = %s "
				"AND Grupo_idGrupo = (SELECT idGrupo FROM Grupos WHERE NomeGrupo = %s) "
				"AND Usuario_idUsuario = %s AND Pastas_idPastas = (SELECT idPasta FROM Pastas WHERE NomePasta = %s)")
		data = (senha,descricao,url,login,nome,NomeGrupo,idUsuario,NomePasta)
		try:
			self.c.execute(query,data)
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute(query,data)
			self.db.commit()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK" , 1	

	def add_unlocked_sharedpassword_db(self,idGrupo,idUsuario,idPasta,idCompartilhado,senha,nome,login,url,descricao):
		query = ("INSERT INTO Passwords (Grupo_idGrupo,Usuario_idUsuario,Pastas_idPastas,idCompartilhado,senha,url,login,descricao,nome)"
				"VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);")
		data = (idGrupo,idUsuario,idPasta,idCompartilhado,senha,url,login,descricao,nome)
		try:
			self.c.execute(query,data)
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute(query,data)
			self.db.commit()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK", 1

	def get_personal_passwords_db(self,username):
		try:
			self.c.execute("SELECT idPassword,senha,nome,login,url,descricao FROM Passwords WHERE Usuario_idUsuario = (SELECT idUsuario FROM Usuarios WHERE username = %s) AND idCompartilhado = 0;",[username])
			passwords = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT idPassword,senha,nome,login,url,descricao FROM Passwords WHERE Usuario_idUsuario = (SELECT idUsuario FROM Usuarios WHERE username = %s) AND idCompartilhado = 0;",[username])
			passwords = self.c.fetchall()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return passwords, 1

	def get_personal_passwords_byfolder_db(self,idPasta,username):
		try:
			self.c.execute("SELECT nome,senha,login,url,descricao,idPassword FROM Passwords WHERE Pastas_idPastas = %s AND Usuario_idUsuario = (SELECT idUsuario FROM Usuarios WHERE username = %s) AND idCompartilhado = 0;",(idPasta,username))
			passwords = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT nome,senha,login,url,descricao,idPassword FROM Passwords WHERE Pastas_idPastas = %s AND Usuario_idUsuario = (SELECT idUsuario FROM Usuarios WHERE username = %s) AND idCompartilhado = 0;",(idPasta,username))
			passwords = self.c.fetchall()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return passwords , 1

	def get_group_passwords_db(self,username):
		try:
			self.c.execute("SELECT idPassword,senha,nome,login,url,descricao FROM Passwords WHERE Usuario_idUsuario = (SELECT idUsuario FROM Usuarios WHERE username = %s) AND idCompartilhado != 0 GROUP BY idCompartilhado;",[username])
			passwords = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT idPassword,senha,nome,login,url,descricao FROM Passwords WHERE Usuario_idUsuario = (SELECT idUsuario FROM Usuarios WHERE username = %s) AND idCompartilhado != 0 GROUP BY idCompartilhado;",[username])
			passwords = self.c.fetchall()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return passwords, 1	

	def get_group_passwords_byfolder_db(self,idPasta,username):
		try:
			self.c.execute("SELECT nome,senha,login,url,descricao,idPassword FROM Passwords WHERE Pastas_idPastas = %s AND Usuario_idUsuario = (SELECT idUsuario FROM Usuarios WHERE username = %s) AND idCompartilhado != 0 GROUP BY idCompartilhado;",(idPasta,username))
			passwords = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT nome,senha,login,url,descricao,idPassword FROM Passwords WHERE Pastas_idPastas = %s AND Usuario_idUsuario = (SELECT idUsuario FROM Usuarios WHERE username = %s) AND idCompartilhado != 0 GROUP BY idCompartilhado;",(idPasta,username))
			passwords = self.c.fetchall()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return passwords , 1

	def get_idcompartilhados_db(self):
		try:
			self.c.execute("SELECT idCompartilhado FROM Passwords ORDER BY 1 DESC;")
			idCompartilhado = self.c.fetchone()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT idCompartilhado FROM Passwords ORDER BY 1 DESC;")
			idCompartilhado = self.c.fetchone()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return idCompartilhado, 1

	def get_usersidbygroup_db(self,NomeGrupo):
		try:
			self.c.execute("SELECT Usuarios_idUsuario FROM Usuario_Grupo WHERE Grupos_idGrupo = (SELECT idGrupo FROM Grupos WHERE NomeGrupo=%s);",[NomeGrupo])
			usersid = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT Usuarios_idUsuario FROM Usuario_Grupo WHERE Grupos_idGrupo = (SELECT idGrupo FROM Grupos WHERE NomeGrupo=%s);",[NomeGrupo])
			usersid = self.c.fetchall()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return usersid, 1

	#pega a chave publica do usuario
	def get_publickey_db(self,idUsuario):
		try:
			self.c.execute("SELECT PublicKey FROM Usuarios WHERE idUsuario = %s;",[idUsuario])
			pk = self.c.fetchone()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT PublicKey FROM Usuarios WHERE idUsuario = %s;",[idUsuario])
			pk = self.c.fetchone()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return pk, 1

	def get_groups_db(self):
		try:
			self.c.execute("SELECT NomeGrupo FROM Grupos")
			groups = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT NomeGrupo FROM Grupos")
			groups = self.c.fetchall()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return groups, 1

	def get_groups_by_id_db(self,idGrupo):
		try:
			self.c.execute("SELECT NomeGrupo FROM Grupos WHERE idGrupo = %s;",[idGrupo])
			groups = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT NomeGrupo FROM Grupos WHERE idGrupo = %s;",[idGrupo])
			groups = self.c.fetchall()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return groups, 1

	def get_group_id_db(self,NomeGrupo):
		try:
			self.c.execute("SELECT idGrupo FROM Grupos WHERE NomeGrupo=%s;",[NomeGrupo])
			idGrupo = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT idGrupo FROM Grupos WHERE NomeGrupo=%s;",[NomeGrupo])
			idGrupo = self.c.fetchall()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return idGrupo , 1

	def get_groups_from_user_db(self,idUsuario):
		try:
			self.c.execute("SELECT Grupos_idGrupo FROM Usuario_Grupo WHERE Usuarios_idUsuario = %s",[idUsuario])
			groups = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT Grupos_idGrupo FROM Usuario_Grupo WHERE Usuarios_idUsuario = %s",[idUsuario])
			groups = self.c.fetchall()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return groups, 1

	def get_pass_by_group_db(self,NomeGrupo,idUsuario):
		query = ("SELECT Grupo_idGrupo,Usuario_idUsuario,Pastas_idPastas,idCompartilhado,senha,nome,login,url,descricao "
				"FROM Passwords "
				"WHERE Grupo_idGrupo = (SELECT idGrupo FROM Grupos WHERE NomeGrupo = %s) "
				"AND idCompartilhado != 0 AND Usuario_idUsuario = %s GROUP BY idCompartilhado;")
		data = (NomeGrupo,idUsuario)
		try:
			self.c.execute(query,data)
			passwd = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute(query,data)
			passwd = self.c.fetchall()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return passwd, 1

	def get_pass_by_group_unlock_db(self,NomeGrupo,idUsuario,idUsuarioLock):
		query = ("SELECT p1.Grupo_idGrupo,p1.Usuario_idUsuario,p1.Pastas_idPastas,p1.idCompartilhado,p1.senha,p1.nome,p1.login,p1.url,p1.descricao FROM Passwords as p1 "
				"WHERE p1.Grupo_idGrupo = (SELECT idGrupo FROM Grupos WHERE NomeGrupo = %s) AND p1.Usuario_idUsuario = %s AND p1.idCompartilhado != 0 AND p1.idCOmpartilhado NOT IN "
				"(SELECT p2.idCompartilhado FROM Passwords as p2 WHERE p2.Grupo_idGrupo = (SELECT idGrupo FROM Grupos WHERE NomeGrupo = %s) "
				"AND p2.idCompartilhado !=0 AND p2.Usuario_idUsuario = %s GROUP BY p2.idCompartilhado) GROUP BY p1.idCompartilhado")

		data = (NomeGrupo,idUsuario,NomeGrupo,idUsuarioLock)
		try:
			self.c.execute(query,data)
			passwd = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute(query,data)
			passwd = self.c.fetchall()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return passwd,1

	def get_folder_db(self,NomePasta):
		try:
			self.c.execute("SELECT idPasta FROM Pastas WHERE NomePasta = %s;",[NomePasta])
			folder = self.c.fetchone()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT idPasta FROM Pastas WHERE NomePasta = %s;",[NomePasta])
			folder = self.c.fetchone()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return folder , 1

	def get_name_folder_db(self,idPasta):
		try:
			self.c.execute("SELECT NomePasta FROM Pastas WHERE idPasta = %s;",[idPasta])
			name = self.c.fetchone()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT NomePasta FROM Pastas WHERE idPasta = %s;",[idPasta])
			name = self.c.fetchone()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return name , 1

	def get_folderbyname_db(self,NomePasta):
		try:
			self.c.execute("SELECT idPasta FROM Pastas WHERE NomePasta = %s;",[NomePasta])
			folder = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT idPasta FROM Pastas WHERE NomePasta = %s;",[NomePasta])
			folder = self.c.fetchall()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return folder, 1 

	def exclude_user_group_db(self,NomeGrupo,username):
		try:
			self.c.execute("DELETE FROM Usuario_Grupo WHERE Grupos_idGrupo = (SELECT idGrupo FROM Grupos WHERE NomeGrupo = %s) AND Usuarios_idUsuario = (SELECT idUsuario FROm Usuarios WHERE username = %s);",(NomeGrupo,username))
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("DELETE FROM Usuario_Grupo WHERE Grupos_idGrupo = (SELECT idGrupo FROM Grupos WHERE NomeGrupo = %s) AND Usuarios_idUsuario = (SELECT idUsuario FROm Usuarios WHERE username = %s);",(NomeGrupo,username))
			self.db.commit()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK",1

	def exclude_password_shared_db(self,idCompartilhado):
		try:
			self.c.execute("DELETE FROM Passwords WHERE idCompartilhado = %s",[idCompartilhado])
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("DELETE FROM Passwords WHERE idCompartilhado = %s",[idCompartilhado])
			self.db.commit()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK" , 1

	def exclude_password_personal_db(self,idPassword):
		try:
			self.c.execute("DELETE FROM Passwords WHERE idPassword = %s",[idPassword])
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("DELETE FROM Passwords WHERE idPassword = %s",[idPassword])
			self.db.commit()
		except MySQLdb.Error, e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK" , 1

	def update_personal_password_db(self,idPassword,nome,senha,descricao,url,login):
		try:
			query = ("UPDATE Passwords SET nome = %s, senha = %s , descricao = %s , url = %s , login = %s WHERE idPassword = %s")
			data = (nome,senha,descricao,url,login,idPassword)
			self.c.execute(query,data)
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute(query,data)
			self.db.commit()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK" , 1

	def update_shared_password_db(self,idPassword,nome,senha,descricao,url,login):
		try:
			query = ("UPDATE Passwords SET nome = %s, senha = %s , descricao = %s , url = %s , login = %s WHERE idPassword = %s")
			data = (nome,senha,descricao,url,login,idPassword)
			self.c.execute(query,data)
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute(query,data)
			self.db.commit()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK" , 1


	def get_passwd_byid_db(self,idPassword):
		try:
			self.c.execute("SELECT nome,senha,url,login,descricao,idCompartilhado,Usuario_idUsuario FROM Passwords WHERE idPassword = %s",[idPassword])
			passwd = self.c.fetchone()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT nome,senha,url,login,descricao,idCompartilhado,Usuario_idUsuario FROM Passwords WHERE idPassword = %s",[idPassword])
			passwd = self.c.fetchone()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return passwd,1

	def get_passwd_byidCompartilhado(self,idCompartilhado):
		try:
			self.c.execute("SELECT idPassword,Usuario_idUsuario,senha,url,login,descricao,nome FROM Passwords WHERE idCompartilhado = %s",[idCompartilhado])
			passwd = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT idPassword,Usuario_idUsuario,senha,url,login,descricao,nome FROM Passwords WHERE idCompartilhado = %s",[idCompartilhado])
			passwd = self.c.fetchall()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return passwd,1		

	def update_publickey(self,idUsuario,pubkey):
		try:
			self.c.execute("UPDATE Usuarios SET PublicKey = %s WHERE idUsuario = %s",(pubkey,idUsuario))
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("UPDATE Usuarios SET PublicKey = %s WHERE idUsuario = %s",(pubkey,idUsuario))
			self.db.commit()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK" , 1

	def update_password_newpubkey(self,idPassword,passwd,nome,login,url,descricao):
		try:
			self.c.execute("UPDATE Passwords SET senha = %s, nome = %s, login = %s, url = %s, descricao = %s WHERE idPassword = %s",(passwd,nome,login,url,descricao,idPassword))
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("UPDATE Passwords SET senha = %s, nome = %s, login = %s, url = %s, descricao = %s WHERE idPassword = %s",(passwd,nome,login,url,descricao,idPassword))
			self.db.commit()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK" , 1

	def get_personalfolder_tree(self,idUsuario):
		try:
			query = ("SELECT node.NomePasta AS name "
					"FROM Pastas AS node, "
					"Pastas AS parent "
					"WHERE node.lft BETWEEN parent.lft AND parent.rgt AND (node.Usuarios_idUsuario = %s) "
					"GROUP BY node.NomePasta "
					"ORDER BY node.lft;")
			data = ([idUsuario])
			self.c.execute(query,data)
			folders = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute(query,data)
			folders = self.c.fetchall()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return folders , 1

	def get_groupfolder_tree(self,NomeGrupo):
		try:
			query = ("SELECT node.NomePasta AS name "
					"FROM Pastas AS node, "
					"Pastas AS parent "
					"WHERE node.lft BETWEEN parent.lft AND parent.rgt "
					"AND node.Grupos_idGrupo = (SELECT idGrupo FROM Grupos WHERE NomeGrupo = %s) "
					"GROUP BY node.NomePasta "
					"ORDER BY node.lft;")
			data = ([NomeGrupo])
			self.c.execute(query,data)
			folders = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute(query,data)
			folders = self.c.fetchall()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return folders , 1

	def get_token(self,idUsuario):
		try:
			self.c.execute("SELECT token FROM Usuarios WHERE idUsuario = %s",[idUsuario])
			token = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT token FROM Usuarios WHERE idUsuario = %s",[idUsuario])
			token = self.c.fetchall()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return token , 1

	def set_token(self,idUsuario,token):
		try:
			self.c.execute("UPDATE Usuarios SET token = %s WHERE idUsuario = %s",(token,idUsuario))
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("UPDATE Usuarios SET token = %s WHERE idUsuario = %s",(token,idUsuario))
			self.db.commit()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK" , 1

	def get_hash(self,idUsuario):
		try:
			self.c.execute("SELECT hash FROM Usuarios WHERE idUsuario = %s",[idUsuario])
			_hash = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("SELECT hash FROM Usuarios WHERE idUsuario = %s",[idUsuario])
			_hash = self.c.fetchall()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return _hash , 1

	def set_hash(self,idUsuario,_hash):
		try:
			self.c.execute("UPDATE Usuarios SET hash = %s WHERE idUsuario = %s",(_hash,idUsuario))
			self.db.commit()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			self.c.execute("UPDATE Usuarios SET hash = %s WHERE idUsuario = %s",(_hash,idUsuario))
			self.db.commit()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return "OK" , 1	

	def search_password(self,idUsuario,folder,name):
		try:
			self.c.execute("SELECT nome,senha,url,login,descricao FROM Passwords WHERE Usuario_idUsuario = %s AND nome = %s AND Pastas_idPastas = (SELECT idPasta FROM Pastas WHERE NomePasta = %s );",(idUsuario,name,folder))
			passwd = self.c.fetchall()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()	
			self.c.execute("SELECT nome,senha,url,login,descricao FROM Passwords WHERE Usuario_idUsuario = %s AND nome = %s AND Pastas_idPastas = (SELECT idPasta FROM Pastas WHERE NomePasta = %s );",(idUsuario,name,folder))
			passwd = self.c.fetchall()
		except MySQLdb.Error,e:
			try:
				message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
			except IndexError:
				message = "MySQL Error: %s" % str(e)
			return message , 0
		return passwd , 1		