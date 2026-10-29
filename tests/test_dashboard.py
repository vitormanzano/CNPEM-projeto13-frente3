"""Testes rápidos do dashboard (sem hardware, sem dependências extras).

Rodar na raiz do projeto:  python tests/test_dashboard.py
(também funciona com pytest)
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "gateway" / "dashboard"))

from hub import Hub  # noqa: E402
from sensor import parse_heart_rate  # noqa: E402


def test_fc_8_bits():
    assert parse_heart_rate(bytes([0x00, 72])) == 72


def test_fc_8_bits_com_rr():
    # flags 0x10 = intervalos RR presentes; FC continua em 8 bits
    assert parse_heart_rate(bytes([0x10, 65, 0x00, 0x04])) == 65


def test_fc_16_bits():
    assert parse_heart_rate(bytes([0x01, 0x2C, 0x01])) == 300


def test_pacote_invalido():
    for ruim in (b"", b"\x00", b"\x01\x10"):
        try:
            parse_heart_rate(ruim)
        except ValueError:
            continue
        raise AssertionError(f"deveria rejeitar {ruim!r}")


def test_rssi_suavizado_e_limpeza():
    hub = Hub()
    hub.update_rssi(-60)
    hub.update_rssi(-80)
    assert -80 < hub.rssi_avg < -60          # EMA fica entre os dois valores
    hub.update_hr(70)
    snap = hub.snapshot()
    assert snap["hr"] == 70 and snap["rssi"] == -80
    hub.clear_signal()
    snap = hub.snapshot()
    assert snap["hr"] is None and snap["rssi"] is None


def test_valor_velho_some():
    hub = Hub()
    hub.update_hr(70)
    hub.hr_ts -= 10                           # leitura de 10 s atrás
    assert hub.snapshot()["hr"] is None


def test_ticker_publica_e_guarda_historico():
    async def cenario():
        hub = Hub()
        fila = hub.subscribe()
        tarefa = asyncio.create_task(hub.run_ticker())
        hub.update_hr(80)
        snap = await asyncio.wait_for(fila.get(), timeout=3)
        tarefa.cancel()
        return hub, snap
    hub, snap = asyncio.run(cenario())
    assert snap["hr"] == 80 and snap["stats"]["max"] == 80
    assert len(hub.history) == 1


if __name__ == "__main__":
    for nome, fn in list(globals().items()):
        if nome.startswith("test_"):
            fn()
            print("ok  ", nome)
