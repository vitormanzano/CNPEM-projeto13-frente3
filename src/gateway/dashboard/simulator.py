"""Fonte simulada: permite ver e testar o dashboard sem a pulseira."""
import asyncio
import math
import random
import time

from hub import Hub


async def run(hub: Hub, seed: int | None = None) -> None:
    rnd = random.Random(seed)
    hub.source = "simulado"
    hub.set_status("conectado", "", device="Simulador · sem pulseira")

    t0 = time.time()
    hr = 74.0
    while True:
        t = time.time() - t0

        # a cada 100 s, 6 s de "perda de conexão" para mostrar como o painel reage
        if 60 < (t % 100) < 66:
            if hub.state != "reconectando":
                hub.clear_signal()
                hub.set_status("reconectando", "Conexão perdida (simulada). Tentando reconectar…")
            await asyncio.sleep(1.0)
            continue
        if hub.state != "conectado":
            hub.set_status("conectado", "")

        alvo = 74 + 10 * math.sin(t / 25)
        hr += (alvo - hr) * 0.15 + rnd.gauss(0, 0.8)
        rssi = -68 + 14 * math.sin(t / 18) + rnd.gauss(0, 2)   # varre de ~-54 a ~-82 dBm
        hub.update_hr(round(hr))
        hub.update_rssi(round(rssi))
        await asyncio.sleep(1.0)
