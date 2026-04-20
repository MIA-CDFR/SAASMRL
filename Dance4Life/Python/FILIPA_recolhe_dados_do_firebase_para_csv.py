import pandas as pd
from services.firebase_service import get_collection_as_df
from config.config import DANCE4LIFE_ACTIVITY_COLLECTION_FIREBASE, DANCE4LIFE_MATCHING_COLLECTION_FIREBASE, DANCE4LIFE_MOVEMENT_RECOMMENDATION_COLLECTION_FIREBASE, DATA_CSV_FOLDER

df = get_collection_as_df(DANCE4LIFE_ACTIVITY_COLLECTION_FIREBASE)
df = df.reindex(columns=sorted(df.columns))
df.to_csv(DATA_CSV_FOLDER + DANCE4LIFE_ACTIVITY_COLLECTION_FIREBASE + ".csv", index=False)

df = get_collection_as_df(DANCE4LIFE_MOVEMENT_RECOMMENDATION_COLLECTION_FIREBASE)
df = df.reindex(columns=sorted(df.columns))
df.to_csv(DATA_CSV_FOLDER + DANCE4LIFE_MOVEMENT_RECOMMENDATION_COLLECTION_FIREBASE + ".csv", index=False)

df = get_collection_as_df(DANCE4LIFE_MATCHING_COLLECTION_FIREBASE)
df = df.reindex(columns=sorted(df.columns))
df.to_csv(DATA_CSV_FOLDER + DANCE4LIFE_MATCHING_COLLECTION_FIREBASE + ".csv", index=False)
