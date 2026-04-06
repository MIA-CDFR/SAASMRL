
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


async def save_activity(data):
    try:
        data_dict = data.dict()
        print("SAVE RAW:", data)
        await db.collection("dance4life_activity").add(data_dict)
        return True  # sucesso
    except Exception as error:
        print(error)
        return False  # falha

# # 🧠 dados inteligentes
# def save_activity(data):
#     print("🔥 SAVE ACTIVITY:", data)
#     db.collection("activities_CB").add(data)


# def save_match(match):
#     print("🔥 SAVE MATCH:", match)
#     db.collection("matches_CB").add(match)


# def save_profile(user_id, q_table):
#     db.collection("profiles_CB").document(user_id).set({
#         "q_table": {str(k): v for k, v in q_table.items()}
#     })

# import firebase_admin
# from firebase_admin import credentials, firestore

# cred = credentials.Certificate("firebase_key.json")
# firebase_admin.initialize_app(cred)

# db = firestore.client()

# def save_activity(data):
#     print("3")
#     db.collection("activities").add(data)

# def get_all_activities():
#     docs = db.collection("activities").get()
#     return [doc.to_dict() for doc in docs]

# def save_match(match):
#     db.collection("matches").add(match)
