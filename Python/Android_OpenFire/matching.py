import math
from firebase_db import get_all_activities


def distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)


def calcular_compatibilidade(a, b):
    score = 0

    if a.get("atividade") == b.get("atividade"):
        score += 0.5

    if a.get("interesse") == b.get("interesse"):
        score += 0.5

    return score


def encontrar_matches(user_data):
    matches = []
    activities = get_all_activities()

    for other in activities:
        if other["userId"] == user_data["userId"]:
            continue

        dist = distance(
            user_data["lat"], user_data["lon"],
            other["lat"], other["lon"]
        )

        if dist > 0.02:
            continue

        score = calcular_compatibilidade(user_data, other)

        if score >= 0.5:
            matches.append({
                "user1": user_data["userId"],
                "user2": other["userId"],
                "score": score
            })

    return matches