import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime


# =========================================================
# CONFIGURAÇÃO FIREBASE
# =========================================================

FIREBASE_KEY_PATH = "firebase_key.json"

cred = credentials.Certificate(FIREBASE_KEY_PATH)
firebase_admin.initialize_app(cred)

db = firestore.client()

# =========================================================
# CAMINHOS DOS DATASETS
# =========================================================

BASE_PATH = Path("./data")

datasets = {
    "dance4life_activity": BASE_PATH / "dance4life_activity_synthetic_5000.csv",
    "dance4life_matching": BASE_PATH / "dance4life_matching_synthetic_5000.csv",
    "dance4life_movement_recommendation": BASE_PATH / "dance4life_movement_recommendation_synthetic_5000.csv",
    "dance4life_invitation": BASE_PATH / "dance4life_invitation_synthetic_5000.csv",
}

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def clean_value(value):
    """
    Limpa valores NaN para compatibilidade com Firestore
    """
    if pd.isna(value):
        return None

    if isinstance(value, np.generic):
        return value.item()

    return value


def convert_row(row):
    """
    Converte uma row pandas para dict compatível Firestore
    """
    data = {}

    for key, value in row.items():
        data[key] = clean_value(value)

    return data


def upload_dataframe(df, collection_name, batch_size=500):
    """
    Upload otimizado para Firestore usando batches
    """

    total = len(df)

    print(f"\n🚀 Upload coleção: {collection_name}")
    print(f"📦 Total registos: {total}")

    batch = db.batch()
    counter = 0

    for index, row in df.iterrows():

        data = convert_row(row)

        # Usa o campo id se existir
        doc_id = str(data.get("id", index))

        doc_ref = db.collection(collection_name).document(doc_id)

        batch.set(doc_ref, data)

        counter += 1

        # Commit batch
        if counter % batch_size == 0:
            batch.commit()
            print(f"✅ {counter}/{total} inseridos")

            batch = db.batch()

    # Commit final
    if counter % batch_size != 0:
        batch.commit()

    print(f"🎉 Upload concluído: {collection_name}")


# =========================================================
# IMPORTAÇÃO DOS DATASETS
# =========================================================

for collection_name, file_path in datasets.items():

    print(f"\n📂 A carregar dataset: {file_path}")

    df = pd.read_csv(file_path)

    upload_dataframe(df, collection_name)

print("\n🔥 Todos os datasets foram inseridos no Firebase!")


# # =====================================================
# # COLEÇÃO
# # =====================================================

# collection_name = "dance4life_invitation"

# collection_ref = db.collection(collection_name)

# updated = 0

# # =====================================================
# # UPDATE BOOLEAN TRUE
# # =====================================================

# docs_true = collection_ref.where("status", "==", True).stream()

# for doc in docs_true:

#     doc.reference.update({
#         "status": "accepted"
#     })

#     updated += 1

# # =====================================================
# # UPDATE STRING "true"
# # =====================================================

# docs_string_true = collection_ref.where("status", "==", "true").stream()

# for doc in docs_string_true:

#     doc.reference.update({
#         "status": "accepted"
#     })

#     updated += 1

print(f"✅ Documentos atualizados: {updated}")