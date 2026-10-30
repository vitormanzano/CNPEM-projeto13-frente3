class Topicos:
    """Coletor: Presença e sinal de vida"""
    @staticmethod
    def presenca_coletor(coletor: str) -> str: return f"coletores/{coletor}/presenca"

    """Coletor: Estado e RSSI"""
    @staticmethod
    def estado_pulseira(coletor: str, pulseira: str) -> str: return f"coletores/{coletor}/pulseiras/{pulseira}"

    """Coletor: Solicitação e liberação de posse"""
    @staticmethod
    def solicitacoes_posse(pulseira: str) -> str: return f"pulseiras/{pulseira}/solicitacoes"

    """Coletor ativo: Leituras de frequência cardíaca"""
    @staticmethod
    def frequencia_cardiaca(pulseira: str) -> str: return f"pulseiras/{pulseira}/frequencia-cardiaca"

    """Coordenador: Coletor responsável ou posse liberada"""
    @staticmethod
    def estado_posse(pulseira: str) -> str: return f"pulseiras/{pulseira}/posse"

    """Coordenador: Comando de handoff com origem e destino"""
    @staticmethod
    def handoff(pulseira: str) -> str: return f"pulseiras/{pulseira}/handoff"

    """Coordenador: Presença e sinal de vida.

    OBS: Esse método não tem nenhum ID pois, no momento atual, existe apenas 1 coordenador.
    """
    @staticmethod
    def presenca_coordenador() -> str: return "coordenador/presenca"

