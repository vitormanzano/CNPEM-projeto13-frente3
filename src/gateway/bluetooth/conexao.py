import asyncio
import logging
import os

from bleak import BleakClient
from bleak.backends.service import BleakGATTServiceCollection
from bleak.exc import BleakDeviceNotFoundError, BleakError

from bluetooth.domain.erros import BluetoothIndisponivel, FalhaConexao
from bluetooth.domain.models import EstadoConexao


CONNECT_TIMEOUT_PADRAO = 20.0


class ConexaoPulseira:
    """Conexão GATT com a pulseira, mantida enquanto o coletor for o responsável por ela."""

    def __init__(self, endereco: str, timeout_conexao: float | None = None) -> None:
        """
        Args:
            endereco (str): Endereço MAC (Linux) ou UUID (macOS) da pulseira.
            timeout_conexao (float | None): Tempo limite da conexão em segundos. Se omitido,
                é lido da variável de ambiente CONNECT_TIMEOUT (padrão de 20 s).
        """
        if timeout_conexao is None:
            timeout_conexao = float(os.getenv("CONNECT_TIMEOUT", CONNECT_TIMEOUT_PADRAO))

        self.endereco = endereco
        self.timeout_conexao = timeout_conexao
        self._estado = EstadoConexao.DESCONECTADO
        self._client: BleakClient | None = None
        self._desconectado = asyncio.Event()
        self._encerramento_solicitado = False

    @property
    def estado(self) -> EstadoConexao:
        """Estado atual da conexão com a pulseira."""
        return self._estado

    @property
    def conectado(self) -> bool:
        return self._client is not None and self._client.is_connected


    @property
    def desconexao_intencional(self) -> bool:
        """Indica se a ultima desconexão foi solicitada pelo coletor"""
        return self._encerramento_solicitado

    @property
    def servicos(self) -> BleakGATTServiceCollection:
        """Serviços GATT da pulseira conectada.

        Raises:
            FalhaConexao: Se a pulseira não estiver conectada.
        """
        if not self.conectado:
            raise FalhaConexao(f"Pulseira {self.endereco} não está conectada")
        return self._client.services

    @property
    def client(self) -> BleakClient:
        """Client Bleak da conexão ativa, para leitura de RSSI e notificações.

        Raises:
            FalhaConexao: Se a pulseira não estiver conectada.
        """
        if not self.conectado:
            raise FalhaConexao(f"Pulseira {self.endereco} não está conectada")
        return self._client

    async def conectar(self) -> None:
        """Estabelece a conexão GATT com a pulseira.

        Raises:
            FalhaConexao: Se não conectar por tempo esgotado, dispositivo ausente ou ocupado.
            BluetoothIndisponivel: Se o Bluetooth estiver desligado ou inacessível.
        """
        if self.conectado:
            logging.info(f"Pulseira {self.endereco} já está conectada")
            return

        logging.info(f"Conectando à pulseira {self.endereco} por até {self.timeout_conexao:g}s")

        self._encerramento_solicitado = False
        self._desconectado.clear()
        self._client = BleakClient(
            self.endereco,
            timeout=self.timeout_conexao,
            disconnected_callback=self._ao_desconectar,
        )

        try:
            await self._client.connect()
        except asyncio.TimeoutError:
            self._registrar_falha(f"tempo esgotado ({self.timeout_conexao:g}s)")
        except BleakDeviceNotFoundError:
            self._registrar_falha("dispositivo ausente")
        except BleakError as e:
            self._registrar_falha(f"dispositivo ocupado ou recusou a conexão: {e}")
        except OSError as e:
            self._client = None
            self._desconectado.set()
            logging.error(f"Bluetooth indisponível [{type(e).__name__}]: {e}")
            raise BluetoothIndisponivel(str(e)) from e

        self._estado = EstadoConexao.CONECTADO
        logging.info(
            f"Estado: {self._estado.value} | Pulseira {self.endereco} | "
            f"{len(self._client.services.services)} serviço(s) disponível(is)"
        )

    async def desconectar(self) -> None:
        """Encerra a conexão de forma controlada, liberando a pulseira para outro coletor."""
        if self._client is None:
            return

        self._encerramento_solicitado = True
        logging.info(f"Desconectando da pulseira {self.endereco}")
        try:
            await self._client.disconnect()
        except BleakError as e:
            logging.warning(f"Erro ao desconectar de {self.endereco} [{type(e).__name__}]: {e}")

        if self._client.is_connected:
            logging.error(
                f"Estado: {self._estado.value} | Erro: {FalhaConexao.codigo} | "
                f"Pulseira {self.endereco} continua conectada após a desconexão"
            )
            raise FalhaConexao(f"Não foi possível liberar a pulseira {self.endereco}")
  
            self._marcar_desconectado()

    async def aguardar_desconexao(self) -> None:
        """Bloqueia até a conexão ser encerrada, seja por queda ou por desconexão controlada."""
        await self._desconectado.wait()

    async def __aenter__(self) -> "ConexaoPulseira":
        await self.conectar()
        return self

    async def __aexit__(self, *_) -> None:
        await self.desconectar()

    def _ao_desconectar(self, _client: BleakClient) -> None:
        if not self._encerramento_solicitado:
            logging.warning(
                f"Estado: {EstadoConexao.DESCONECTADO.value} | Pulseira {self.endereco} desconectou inesperadamente"
            )
        self._marcar_desconectado()

    def _marcar_desconectado(self) -> None:
        if self._estado is EstadoConexao.DESCONECTADO and self._desconectado.is_set():
            return
        self._estado = EstadoConexao.DESCONECTADO
        self._desconectado.set()
        if self._encerramento_solicitado:
            logging.info(f"Estado: {self._estado.value} | Pulseira {self.endereco} liberada")

    def _registrar_falha(self, motivo: str) -> None:
        self._client = None
        self._estado = EstadoConexao.DESCONECTADO
        self._desconectado.set()
        logging.error(f"Estado: {self._estado.value} | Erro: {FalhaConexao.codigo} | Pulseira {self.endereco}: {motivo}")
        raise FalhaConexao(motivo)
