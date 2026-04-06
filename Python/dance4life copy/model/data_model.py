from pydantic import BaseModel, Field
from typing import List, Optional


class SensorActivityData(BaseModel):
    utilizador_id: str  # obrigatório
    utilizador_nome: Optional[str] = None
    acc: Optional[float] = None
    hr: Optional[int] = None
    ritmo: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class MatchingData(BaseModel):
    emparelhado_utilizador_id: Optional[str] = None


class CalculatedActivityData(BaseModel):
    actividade: Optional[str] = None
    interesse: Optional[float] = None
    timestamp: Optional[str] = None
    timestamp_dia_semana: Optional[str] = None
    timestamp_dia_periodo: Optional[str] = None
    timestamp_hora: Optional[int] = None
    timestamp_dia: Optional[int] = None
    timestamp_mes: Optional[str] = None
    timestamp_ano: Optional[int] = None


class EnvironmentData(BaseModel):
    musica_id: Optional[str] = None
    musica_nome: Optional[str] = None
    musica_banda: Optional[str] = None
    musica_tipo_id: Optional[str] = None
    musica_tipo_nome: Optional[str] = None
    quantidade_pessoas_sala: Optional[int] = None
    quantidade_pessoas_sala_actividade: Optional[int] = None
    quantidade_pessoas_sala_paradas: Optional[int] = None
    atividade_media_sala: Optional[float] = None
    interesse_medio_sala: Optional[float] = None
    matching_list_sal: List[str] = Field(default_factory=list)


class WeatherData(BaseModel):
    temperatura: Optional[float] = None
    humidade: Optional[float] = None


class ActivityData(BaseModel):
    sensor_activity_data: SensorActivityData
    matching_data: Optional[MatchingData] = None
    calculated_activity_data: Optional[CalculatedActivityData] = None
    environment_data: Optional[EnvironmentData] = None
    weather_data: Optional[WeatherData] = None