# 	https://home.openweathermap.org/api_keys   --> MIA_SAASMRL: 713312eb18af19cb90bc032a1e0660a5
OPENWEATHER_API_KEY = "b18771a2623d1ed24b7697f1e6c193c8"

# https://explore.openaq.org/account
OPENAQ_API_KEY = "809ac4a96dd931c68c08a3da03be86ba81c53b9b04216e2df8111f63d91cc54d"

# https://developer.tomtom.com/user/me/apps; https://my.tomtom.com/keys
TOMTOM_API_KEY = "bhnS08haIcnuiQ21NWDW1PisA7f5UYcX"

LAT = 41.1579   # Porto
LON = -8.6291

FIREBASE_CREDENTIALS = "firebase_key.json"



COLLECTORS_INTERVAL = 300  # 5 minutos

COLLECTORS_WEATHER_COLLECTION_FIREBASE  = "collectors_weather"
COLLECTORS_AIR_QUALITY_COLLECTION_FIREBASE = "collectors_air_quality"
COLLECTORS_TRAFFIC_COLLECTION_FIREBASE = "collectors_traffic"

DANCE4LIFE_ACTIVITY_COLLECTION_FIREBASE = "dance4life_activity"
DANCE4LIFE_ACTIVITY_COLLECTION_FIREBASE = "dance4life_movement_recommendation"


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

class AgentPerformatives:
    REQUEST = "request"
    AGREE = "agree"
    INFORM = "inform"
    FAILURE = "failure"