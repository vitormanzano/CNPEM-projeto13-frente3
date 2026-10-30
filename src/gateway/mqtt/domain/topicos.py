class Topicos:
    @staticmethod
    def presenca_coletor(coletor: str) -> str:
        """Coletor: Presença e sinal de vida"""
        return f"coletores/{coletor}/presenca"

    @staticmethod
    def estado_coletor(coletor: str, pulseira: str) -> str:
        """Coletor: Estado e RSSI"""
        return f"coletores/{coletor}/pulseiras/{pulseira}"

    @staticmethod
    def solicitacoes_posse(pulseira: str) -> str:
        """Coletor: Solicitação e liberação de posse"""
        return f"pulseiras/{pulseira}/solicitacoes"

    @staticmethod
    def frequencia_cardiaca(pulseira: str) -> str:
        """Coletor ativo: Leituras de frequência cardíaca"""
        return f"pulseiras/{pulseira}/frequencia-cardiaca"

    @staticmethod
    def estado_posse(pulseira: str) -> str:
        """Coordenador: Coletor responsável ou posse liberada"""
        return f"pulseiras/{pulseira}/posse"

    @staticmethod
    def handoff(pulseira: str) -> str:
        """Coordenador: Comando de handoff com origem e destino"""
        return f"pulseiras/{pulseira}/handoff"

    @staticmethod
    def presenca_coordenador() -> str:
        """Coordenador: Presença e sinal de vida.

        OBS: Esse método não tem nenhum ID pois, no momento atual, existe apenas 1 coordenador.
        """
        return "coordenador/presenca"
