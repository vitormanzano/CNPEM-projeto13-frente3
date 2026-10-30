import asyncio
import logging
import os

from bluetooth.conexao import ConexaoPulseira
from bluetooth.domain.erros import BluetoothIndisponivel, FalhaConexao
from bluetooth.reconexao import manter_conexao

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    endereco = os.getenv("TARGET_ADDRESS")
    if not endereco:
        logging.error("Defina a variável de ambiente TARGET_ADDRESS com o endereço da pulseira.")
        return

    conexao = ConexaoPulseira(endereco)
    try:
        await manter_conexao(conexao)
    except (FalhaConexao, BluetoothIndisponivel) as e:
        logging.error(f"Erro: {e.codigo} | {e}")
    finally:
        await conexao.desconectar()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
