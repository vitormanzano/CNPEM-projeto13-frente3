"""Leitura BLE da Polar Verity Sense: frequência cardíaca + força do sinal (RSSI).

- FC: serviço padrão Heart Rate (0x180D), característica 0x2A37, por notificação.
- RSSI: `client.get_rssi()` com a conexão ativa (mesmo método usado em
  bluetooth/scanner.py). Se a plataforma não oferecer isso, cai para o RSSI dos
  anúncios (advertising) vistos por um scanner em paralelo.

`bleak` é importado só dentro de `run()`, então o resto do dashboard (e o modo
simulado) funciona mesmo sem o Bleak instalado.
"""
import asyncio

from hub import Hub

HR_MEASUREMENT_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
RETRY_S = 3.0


def parse_heart_rate(data: bytes) -> int:
    """Decodifica a característica Heart Rate Measurement (0x2A37).

    Byte 0 = flags; bit 0 indica se a FC vem em 8 bits (0) ou 16 bits (1).
    """
    if len(data) < 2:
        raise ValueError("pacote de FC curto demais")
    if data[0] & 0x01:
        if len(data) < 3:
            raise ValueError("pacote de FC de 16 bits incompleto")
        return int.from_bytes(data[1:3], "little")
    return data[1]


class PolarSensor:
    def __init__(self, hub: Hub, address: str | None = None, name_hint: str = "Polar") -> None:
        self.hub = hub
        self.address = address or None
        self.name_hint = name_hint.lower()
        self._adv_rssi: int | None = None
        self._use_scan_rssi = False
        self._target_address: str | None = None

    # ------------------------------------------------------------------
    async def run(self) -> None:
        try:
            import bleak  # noqa: F401
        except ImportError:
            self.hub.set_status("erro", "Bleak não instalado. Rode: pip install -r requirements.txt")
            return

        while True:
            try:
                await self._session()
            except asyncio.CancelledError:
                raise
            except Exception as erro:  # noqa: BLE001 - qualquer falha => tenta de novo
                self.hub.clear_signal()
                self.hub.set_status("reconectando", f"{type(erro).__name__}: {erro}")
            await asyncio.sleep(RETRY_S)

    # ------------------------------------------------------------------
    async def _find_device(self):
        from bleak import BleakScanner

        if self.address:
            return await BleakScanner.find_device_by_address(self.address, timeout=10.0)

        def combina(device, adv) -> bool:
            nome = (adv.local_name or device.name or "").lower()
            return self.name_hint in nome

        return await BleakScanner.find_device_by_filter(combina, timeout=10.0)

    def _on_adv(self, device, adv) -> None:
        if self._target_address and device.address == self._target_address:
            self._adv_rssi = adv.rssi

    async def _read_rssi(self, client) -> int | None:
        if not self._use_scan_rssi:
            try:
                return await client.get_rssi()
            except (AttributeError, NotImplementedError):
                self._use_scan_rssi = True   # plataforma sem RSSI de conexão
            except Exception:  # noqa: BLE001 - leitura isolada falhou, tenta no próximo ciclo
                return None
        return self._adv_rssi

    async def _session(self) -> None:
        from bleak import BleakClient, BleakScanner

        hub = self.hub
        hub.clear_signal()
        hub.set_status("procurando", "Procurando a pulseira (ligada e fora de outros apps)…")
        device = await self._find_device()
        if device is None:
            hub.set_status("procurando", "Pulseira não encontrada. Verifique se está ligada e ao alcance.")
            return

        self._target_address = device.address
        self._adv_rssi = None
        self._use_scan_rssi = False
        nome = device.name or "Polar"
        hub.set_status("conectando", f"Conectando a {nome}…", device=f"{nome} · {device.address}")

        desconectou = asyncio.Event()

        def ao_desconectar(_client) -> None:
            desconectou.set()

        def ao_receber_fc(_sender, data: bytearray) -> None:
            try:
                hub.update_hr(parse_heart_rate(bytes(data)))
            except ValueError:
                pass  # pacote malformado: ignora

        scanner = None
        try:
            async with BleakClient(device, disconnected_callback=ao_desconectar, timeout=20.0) as client:
                await client.start_notify(HR_MEASUREMENT_UUID, ao_receber_fc)
                hub.set_status("conectado", "")

                while client.is_connected and not desconectou.is_set():
                    rssi = await self._read_rssi(client)
                    if self._use_scan_rssi and scanner is None:
                        scanner = BleakScanner(detection_callback=self._on_adv)
                        await scanner.start()
                    if rssi is not None:
                        hub.update_rssi(rssi)
                    try:
                        await asyncio.wait_for(desconectou.wait(), timeout=1.0)
                    except asyncio.TimeoutError:
                        pass
        finally:
            if scanner is not None:
                try:
                    await scanner.stop()
                except Exception:  # noqa: BLE001
                    pass

        hub.clear_signal()
        hub.set_status("reconectando", "Conexão perdida. Tentando reconectar…")
