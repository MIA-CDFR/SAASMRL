import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def save_activity(data):
    print("3")
    db.collection("activities").add(data)

def get_all_activities():
    docs = db.collection("activities").get()
    return [doc.to_dict() for doc in docs]

def save_match(match):
    db.collection("matches").add(match)