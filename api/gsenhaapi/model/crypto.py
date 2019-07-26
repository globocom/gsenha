# -*- coding: utf-8 -*-
import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

from gsenhaapi.controller.databaseController import DatabaseController
from gsenhaapi.exceptions import CryptoError

class Crypto:

	def __init__(self,database):
		self.db = database

	def get_pubkey(self,userdb):
		tmp = self.db.get_pubkey(userdb)
		
		pk_s = str(tmp[0])
		tmp = pk_s.strip("''(),")
		tmp2 = tmp.split(",")
		e = int(tmp2[1])
		n = int(tmp2[0])
		numbers = rsa.RSAPublicNumbers(e, n)
		pubkey = numbers.public_key(default_backend())
	
		return pubkey

	def load_pubkey(self,keydata):
		try:
			pubkey = load_pem_public_key(keydata, backend=default_backend())
		except ValueError:
			raise CryptoError("failed to read public key",500)
		except Exception:
			raise CryptoError("failed to get public key",500)

		if pubkey.key_size != 4096:
			raise CryptoError("public key must be 4096 bits",400)

		return pubkey

	def load_privkey(self,privk_s):
		try:
			privkey = load_pem_private_key(privk_s, password=None, backend=default_backend())
		except ValueError:
			raise CryptoError("Failed to load private key. Only PEM format is supported.")
		except cryptography.exceptions.UnsupportedAlgorithm:
			raise CryptoError("Unsupported Algorithm",500)
		return privkey

	def generate_privkey(self):
		private_key = rsa.generate_private_key(public_exponent=65537,key_size=4096,backend=default_backend())
		return private_key

	def generate_pem_public(self,public_key):
		return public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)

	def generate_pem_private(self,private_key):
		return private_key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.TraditionalOpenSSL,encryption_algorithm=serialization.NoEncryption())
