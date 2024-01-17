import os
from dotenv import load_dotenv


load_dotenv()


DATABASE_CONNECTION_STRING = os.environ.get('DATABASE_CONNECTION_STRING')
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
PLACEHOLDER_USER_EMAIL = "placeholder@softwarequizzes.com"
ADMIN_EMAIL = "raaj.akshar@gmail.com"
REDIS_HOST = os.environ['REDIS_HOST']
REDIS_PORT = os.environ['REDIS_PORT']
DEFAULT_SUBDOMAINS = ['python', 'javascript', 'sql']
ES_ENDPOINT = os.environ.get('ES_ENDPOINT')
ES_AUTH_TOKEN = os.environ.get('ES_AUTH_TOKEN')
