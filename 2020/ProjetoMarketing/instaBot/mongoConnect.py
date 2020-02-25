import pymongo
import os

def connect():
    userName = os.getenv("USERNAME_MONGODB")
    pwd = os.getenv("PASSWORD_MONGODB")
    conexaoDB = pymongo.MongoClient(f"mongodb+srv://{userName}:{pwd}@datainstagram-s6xj1.mongodb.net/test?retryWrites=true&w=majority")
    myDB = conexaoDB['InstagramMarketing']
    return conexaoDB, myDB