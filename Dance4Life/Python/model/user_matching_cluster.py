import math
from typing import Any, Dict, List, Optional, Tuple


class UserMatchingClusterModel:
    """Simple in-memory clustering model for dance partner matchmaking.

    It groups users by a compact feature vector and then ranks candidates within
    the same cluster by music preference, distance, and rhythm/heart-rate affinity.
    """

    def __init__(
        self,
        n_clusters: int = 4,
        max_distance_km: float = 8.0,
        min_similarity: float = 0.45,
        max_kmeans_iter: int = 20,
    ) -> None:
        self.n_clusters = max(2, n_clusters)
        self.max_distance_km = max_distance_km
        self.min_similarity = min_similarity
        self.max_kmeans_iter = max_kmeans_iter
        self.user_profiles: Dict[str, Dict[str, Any]] = {}

    def process_matching_request(self, payload: Dict[str, Any], top_k: int = 3) -> Dict[str, Any]:
        user_id = self._extract_user_id(payload)
        if not user_id:
            enriched = payload.copy()
            enriched["matching_result"] = {
                "status": "error",
                "message": "Missing user identifier (user_id or device_id).",
                "matches": [],
            }
            return enriched

        self._upsert_profile(user_id, payload)

        cluster_assignments = self._cluster_assignments()
        cluster_id = cluster_assignments.get(user_id, 0)
        matches = self._rank_candidates(user_id, cluster_assignments, top_k=top_k)

        enriched_payload = payload.copy()
        enriched_payload["matching_result"] = {
            "status": "ok",
            "cluster_id": f"cluster_{cluster_id}",
            "total_known_users": len(self.user_profiles),
            "matches": matches,
        }

        if matches:
            enriched_payload["matched_user_id"] = matches[0]["user_id"]
        else:
            enriched_payload["matched_user_id"] = None

        return enriched_payload

    def _upsert_profile(self, user_id: str, payload: Dict[str, Any]) -> None:
        profile = {
            "user_id": user_id,
            "latitude": self._to_float(payload.get("latitude")),
            "longitude": self._to_float(payload.get("longitude")),
            "hr": self._to_float(payload.get("hr")),
            "ritmo": self._to_float(payload.get("ritmo")),
            "music_genre": self._get_music_value(payload, ["music_genre", "musica_tipo_nome", "musica_tipo_id"]),
            "music_name": self._get_music_value(payload, ["music_name", "musica_nome", "musica_id"]),
        }
        profile["features"] = self._build_feature_vector(profile)
        self.user_profiles[user_id] = profile

    def _build_feature_vector(self, profile: Dict[str, Any]) -> List[float]:
        lat = (profile.get("latitude") or 0.0) / 90.0
        lon = (profile.get("longitude") or 0.0) / 180.0
        hr = min(max((profile.get("hr") or 0.0) / 220.0, 0.0), 1.0)
        ritmo = min(max((profile.get("ritmo") or 0.0) / 3.0, 0.0), 1.0)

        genre = (profile.get("music_genre") or "").strip().lower()
        genre_bucket = (sum(ord(ch) for ch in genre) % 997) / 997.0 if genre else 0.0

        return [lat, lon, hr, ritmo, genre_bucket]

    def _cluster_assignments(self) -> Dict[str, int]:
        user_ids = list(self.user_profiles.keys())
        if not user_ids:
            return {}
        if len(user_ids) == 1:
            return {user_ids[0]: 0}

        vectors = [self.user_profiles[user_id]["features"] for user_id in user_ids]
        n_clusters = min(self.n_clusters, len(vectors))
        centroids = [vectors[i][:] for i in range(n_clusters)]

        assignments: List[int] = [0 for _ in vectors]
        for _ in range(self.max_kmeans_iter):
            changed = False

            for i, vector in enumerate(vectors):
                nearest_cluster = self._nearest_centroid(vector, centroids)
                if assignments[i] != nearest_cluster:
                    changed = True
                    assignments[i] = nearest_cluster

            if not changed:
                break

            for cidx in range(n_clusters):
                members = [vectors[i] for i, a in enumerate(assignments) if a == cidx]
                if not members:
                    continue
                centroids[cidx] = [sum(col) / len(col) for col in zip(*members)]

        return {user_id: assignments[i] for i, user_id in enumerate(user_ids)}

    def _rank_candidates(self, user_id: str, assignments: Dict[str, int], top_k: int) -> List[Dict[str, Any]]:
        if user_id not in self.user_profiles:
            return []

        target_profile = self.user_profiles[user_id]
        target_cluster = assignments.get(user_id, 0)

        candidates: List[Tuple[float, Dict[str, Any]]] = []
        for other_user_id, profile in self.user_profiles.items():
            if other_user_id == user_id:
                continue
            if assignments.get(other_user_id, -1) != target_cluster:
                continue

            music_score = self._music_score(target_profile, profile)
            distance_km = self._distance_km(target_profile, profile)
            distance_score = max(0.0, 1.0 - (distance_km / self.max_distance_km))
            vitals_score = self._vitals_score(target_profile, profile)

            score = 0.45 * music_score + 0.35 * distance_score + 0.20 * vitals_score
            if score < self.min_similarity:
                continue

            match = {
                "user_id": other_user_id,
                "score": round(score, 3),
                "distance_km": round(distance_km, 3),
                "cluster_id": f"cluster_{target_cluster}",
                "same_music": music_score >= 0.95,
            }
            candidates.append((score, match))

        candidates.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in candidates[:top_k]]

    def _music_score(self, p1: Dict[str, Any], p2: Dict[str, Any]) -> float:
        g1 = (p1.get("music_genre") or "").strip().lower()
        g2 = (p2.get("music_genre") or "").strip().lower()
        n1 = (p1.get("music_name") or "").strip().lower()
        n2 = (p2.get("music_name") or "").strip().lower()

        if g1 and g2 and g1 == g2:
            return 1.0
        if n1 and n2 and n1 == n2:
            return 0.9
        if g1 and g2 and (g1 in g2 or g2 in g1):
            return 0.7
        return 0.2

    def _vitals_score(self, p1: Dict[str, Any], p2: Dict[str, Any]) -> float:
        hr1 = p1.get("hr")
        hr2 = p2.get("hr")
        ritmo1 = p1.get("ritmo")
        ritmo2 = p2.get("ritmo")

        score_parts = []
        if hr1 is not None and hr2 is not None:
            score_parts.append(max(0.0, 1.0 - abs(hr1 - hr2) / 70.0))
        if ritmo1 is not None and ritmo2 is not None:
            score_parts.append(max(0.0, 1.0 - abs(ritmo1 - ritmo2) / 2.0))

        if not score_parts:
            return 0.5
        return sum(score_parts) / len(score_parts)

    def _distance_km(self, p1: Dict[str, Any], p2: Dict[str, Any]) -> float:
        lat1 = p1.get("latitude")
        lon1 = p1.get("longitude")
        lat2 = p2.get("latitude")
        lon2 = p2.get("longitude")

        if None in (lat1, lon1, lat2, lon2):
            return self.max_distance_km

        r = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(d_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2.0) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c

    def _nearest_centroid(self, vector: List[float], centroids: List[List[float]]) -> int:
        best_idx = 0
        best_dist = float("inf")

        for idx, centroid in enumerate(centroids):
            dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(vector, centroid)))
            if dist < best_dist:
                best_dist = dist
                best_idx = idx

        return best_idx

    def _extract_user_id(self, payload: Dict[str, Any]) -> Optional[str]:
        for key in ("user_id", "device_id", "id"):
            value = payload.get(key)
            if value:
                return str(value)
        return None

    def _to_float(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _get_music_value(self, payload: Dict[str, Any], keys: List[str]) -> Optional[str]:
        for key in keys:
            value = payload.get(key)
            if value:
                return str(value)
        return None
