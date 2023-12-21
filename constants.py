import os
from dotenv import load_dotenv


load_dotenv()


DATABASE_CONNECTION_STRING = os.environ.get('DATABASE_CONNECTION_STRING')
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
