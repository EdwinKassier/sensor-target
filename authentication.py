"""This is a wrapper for a decorator that we can use on a request"""
from functools import wraps

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth

import os

import traceback

# Use a the given service account
if os.path.exists('credentials.json'):
	cred = credentials.Certificate('credentials.json')
	firebase_admin.initialize_app(cred)

from flask import abort, current_app, request

def check_auth(view_function):
	"""This is used in the core app as part of a zero trust model to ensure users are authorized
	This would be part of a larger system where we also ensure
	only valid sources of queries can query the api in the first place (part of our cloud infrastructure)"""
	@wraps(view_function)
	#This decorator allows us to globally call the function to check auth regardless of source
	def decorated_function(*args, **kwargs):
		"""checks for verified request using firebase auth, this also gracefully handles anonymous user in the case of front ends where the user can't login"""
		try:
			print("checking authorization...")
			headers = request.headers
			bearer = headers.get("Authorization")
			token = bearer.split()[1]
			print("token", token)

			decoded_token = auth.verify_id_token(token)
			uid = decoded_token["uid"]
			print("uid", uid)
			return view_function(*args, **kwargs)

		except Exception as e:
			print(traceback.format_exc())
			abort(401)



	return decorated_function
