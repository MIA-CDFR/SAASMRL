# 	https://home.openweathermap.org/api_keys   --> MIA_SAASMRL: 713312eb18af19cb90bc032a1e0660a5
OPENWEATHER_API_KEY = "b18771a2623d1ed24b7697f1e6c193c8"

FIREBASE_CREDENTIALS = "firebase_key.json"

COLLECTORS_INTERVAL = 300  # 5 minutos

DANCE4LIFE_ACTIVITY_COLLECTION_FIREBASE = "dance4life_activity"
DANCE4LIFE_MOVEMENT_RECOMMENDATION_COLLECTION_FIREBASE = "dance4life_movement_recommendation"
DANCE4LIFE_MATCHING_COLLECTION_FIREBASE = "dance4life_matching"
DANCE4LIFE_INVITATION_COLLECTION_FIREBASE = "dance4life_invitation"

DATA_CSV_FOLDER = "data/"

AGENT_PASSWORD = "password"

class AgentAddresses:
    API_AGENT = "api_agent@localhost"
    SENSOR_AGENT = "sensor_agent@localhost"
    COORDINATOR_AGENT = "coordinator_agent@localhost"
    ENVIRONMENT_AGENT = "environment_agent@localhost"
    HAR_AGENT = "har_agent@localhost"
    DATABASE_AGENT = "database_agent@localhost"
    MATCHING_AGENT = "matching_agent@localhost"

class AgentOntologies:
    SENSOR_ACTIVITY = "sensor_activity"
    MOVEMENT_RECOMMENDATION = "movement_recommendation"
    MATCHING = "matching"

class AgentPerformatives:
    REQUEST = "request"
    AGREE = "agree"
    INFORM = "inform"
    FAILURE = "failure"

class SeververConfig:
    SERVER_HOSTNAME = "localhost"
    SERVER_PORT = "5000" 