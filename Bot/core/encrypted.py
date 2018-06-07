#!/usr/bin/python
# -*- coding: UTF-8 -*-
import base64
import binascii

import rsa
from requests import Session


class Encryption:

	def __init__(self):
		self.public_key_n = "F142553977AFB4FE0D5916E734FB5BEA2AFC7DE6D6023F4FCCB5ABC3F8E1B68400BCF53BADF7F308632E152BAF9" \
		                    "D1558C8246A7BC18D7DBE466AE5B14443A3210B6CA219393A66200CD6101DE00AE6E0312173B4D0EDA02A766363" \
		                    "66E832D1A73F8B74F9100E28068CA0FD32AC16C249A721033C344867A37AA87A12D195FA6B"

	def rsa_encrypted(self, password):
		base64_password = base64.b64encode(password.encode())
		public_key = rsa.PublicKey(int(self.public_key_n, 16), 0x010001)
		encrypted_password = rsa.encrypt(base64_password, public_key)
		encrypted_password = binascii.hexlify(bytearray(encrypted_password))
		return encrypted_password

	def fuck(self, encrypted_password):
		if not isinstance(encrypted_password, bytes):
			encrypted_password = bytes(encrypted_password, encoding="utf8")
		result = ""
		digit_str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
		i = 0
		index = 0
		digit = 0
		while i < len(encrypted_password):
			curr_byte = encrypted_password[i]
			if curr_byte < 0:
				curr_byte += 256
			if index > 3:
				next_byte = 0
				if (i + 1) < len(encrypted_password):
					next_byte = encrypted_password[i + 1]
					if next_byte < 0:
						next_byte += 256
				digit = curr_byte & (0xFF >> index)
				index = (index + 5) % 8
				digit <<= index
				digit |= (next_byte >> (8 - index))
				i += 1
			else:
				digit = (curr_byte >> (8 - (index + 5))) & 0x1F
				index = (index + 5) % 8
				if index == 0:
					i += 1
			result += digit_str[digit]
		return result.lower()

	def fucker(self, data):
		return self.fuck(data)

	def conversion(self, data):
		s2 = self.fucker(data)
		return self.fuck(s2)

	def encrypted(self, data):
		info = self.rsa_encrypted(password=data)
		password = self.conversion(info)
		return password

	def test(self):
		info = input("Input password:")
		try:
			print(info)
			info = self.rsa_encrypted(password=info)
			print(info)
			password = self.conversion(info)
			print(password)
			print(self.login(password))
		except Exception as e:
			print(e)
		finally:
			input("encrypted done")

	def login(self, pwd):
		header = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
			'Accept': 'text/plain, */*'}
		session = Session()
		session.get('http://hh.zzt333.com/Default.aspx')
		response = session.post(
			'http://hh.zzt333.com/MemberLogin.aspx?User=ss888&Pwd=%s' % pwd,
			headers=header
		)
		return response.text
