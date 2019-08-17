import bcrypt
import base64
import secrets
import constants


def get_new_token():
    return secrets.token_hex()


def hash_password(password):
    to_hash = password + constants.SALT
    return base64.b64encode(bcrypt.hashpw(to_hash.encode('utf-8'), bcrypt.gensalt())).decode('utf-8')


def check_password(password, hashed_password):
    to_check = password + constants.SALT
    return bcrypt.checkpw(to_check.encode('utf-8'), base64.b64decode(hashed_password.encode('utf-8')))
