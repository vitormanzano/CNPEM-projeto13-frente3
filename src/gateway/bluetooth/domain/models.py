from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

class EstadoConexao(Enum):
    CONECTADO = "conectado"
    DESCONECTADO = "desconectado"
    CONEXAO_FRACA = "conexao-fraca"
    NAO_ENCONTRADO = "nao-encontrado"


@dataclass(frozen=True)
class Pulseira:
    endereco: str
    nome: str | None
    rssi: int | None = None


@dataclass(frozen=True)
class LeituraRSSI:
    endereco: str
    rssi: int | None = None
    estado: EstadoConexao
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

