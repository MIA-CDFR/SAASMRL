
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

from config.config import DANCE4LIFE_ACTIVITY_COLLECTION_FIREBASE, DANCE4LIFE_INVITATION_COLLECTION_FIREBASE, DANCE4LIFE_MATCHING_COLLECTION_FIREBASE, DANCE4LIFE_MOVEMENT_RECOMMENDATION_COLLECTION_FIREBASE

cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def save_data_from_collectors(collection, data):
    db.collection(collection).add(data)

async def save_activity(data):
    try:
        #data_dict = data.dict()
        print("SAVE ACTIVITY:", data)
        db.collection(DANCE4LIFE_ACTIVITY_COLLECTION_FIREBASE).add(data)
        print(f"---------------SUCCESS: Activity saved------------------")
        return True  # sucesso
    except Exception as error:
        print(f"---------------ERROR: {error}------------------")
        return False  # falha

async def save_movement_recommendation(data):
    try:
        print("SAVE MOVEMENT RECOMMENDATION:", data)
        db.collection(DANCE4LIFE_MOVEMENT_RECOMMENDATION_COLLECTION_FIREBASE).add(data)
        print(f"---------------SUCCESS: Movement recommendation saved------------------")
        return True  # sucesso
    except Exception as error:
        print(f"---------------ERROR: {error}------------------")
        return False  # falha

async def save_matching(data):
    try:
        print("SAVE MATCHING:", data)
        db.collection(DANCE4LIFE_MATCHING_COLLECTION_FIREBASE).add(data)
        print(f"---------------SUCCESS: Matching saved------------------")
        return True  # sucesso
    except Exception as error:
        print(f"---------------ERROR: {error}------------------")
        return False  # falha

async def save_invitation(data):
    try:
        print("SAVE INVITATION:", data)
        db.collection(DANCE4LIFE_INVITATION_COLLECTION_FIREBASE).add(data)
        print(f"---------------SUCCESS: Invitation saved------------------")
        return True  # sucesso
    except Exception as error:
        print(f"---------------ERROR: {error}------------------")
        return False  # falha
    
def get_collection_as_df(collection_name):
    docs = db.collection(collection_name).stream()

    data = []
    for doc in docs:
        doc_dict = doc.to_dict()
        doc_dict["id"] = doc.id  # opcional: guardar ID
        data.append(doc_dict)

    df = pd.DataFrame(data)
    return df


