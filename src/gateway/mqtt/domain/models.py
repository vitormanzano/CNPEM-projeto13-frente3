from enum import Enum
from datetime import datetime, timezone
from dataclasses import dataclass, field

VERSAO_FORMATO = 1

class TipoMensagem(Enum):
    PRESENCA            = "presenca"
    ESTADO_PULSEIRA     = "estado-pulseira"
    SOLICITACAO_POSSE   = "solicitacao-posse"
    FREQUENCIA_CARDIACA = "frequencia-cardiaca"
    POSSE               = "posse"
    HANDOFF             = "handoff"


@dataclass(frozen=True)
class Mensagem:
    tipo: TipoMensagem
    origem: str # Id coletor ou id coordenador
    conteudo: dict
    versao: int = VERSAO_FORMATO
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


