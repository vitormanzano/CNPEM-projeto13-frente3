import asyncio
from bleak import BleakClient
from bleak.exc import BleakError
import traceback
from bleak import BleakScanner
import logging

from bluetooth.domain.erros import BluetoothIndisponivel
from bluetooth.domain.models import DispositivoBLE

TARGET_ADDRESS="84B49860-9C1B-D2AC-9ABD-3074E2B20F9F"

SCAN_TIMEOUT_PADRAO = 10.0
NOME_PADRAO = "Desconhecido / Oculto"


async def find_all_local_devices(timeout: float = SCAN_TIMEOUT_PADRAO) -> list[DispositivoBLE]:
    """Lista os dispositivos BLE anunciando ao alcance do coletor (RF01).

    Cada dispositivo aparece uma única vez (o Bleak agrupa por endereço),
    com o RSSI do anúncio mais recente.

    Args:
        timeout (float): Duração da varredura em segundos.

    Returns:
        list[DispositivoBLE]: Dispositivos ordenados do sinal mais forte para o mais fraco.
            Lista vazia caso nenhum seja encontrado.

    Raises:
        BluetoothIndisponivel: Se o Bluetooth estiver desligado ou inacessível.
    """
    logging.info(f"Iniciando varredura BLE por {timeout:g}s")

    try:
        devices_dict = await BleakScanner.discover(return_adv=True, timeout=timeout)
    except (BleakError, OSError) as e:
        logging.error(f"Falha ao iniciar varredura BLE [{type(e).__name__}]: {e}")
        raise BluetoothIndisponivel(str(e)) from e

    dispositivos = [
        DispositivoBLE(
            endereco=address,
            nome=adv_data.local_name or dev.name or NOME_PADRAO,
            rssi=adv_data.rssi,
        )
        for address, (dev, adv_data) in devices_dict.items()
    ]
    dispositivos.sort(key=lambda d: d.rssi, reverse=True)

    logging.info(f"Varredura concluída: {len(dispositivos)} dispositivo(s) encontrado(s)")
    return dispositivos


async def find_by_alternative_criteria(target_name="Polar Verity", target_service_uuid=None):
    # Retorna o dispositivo e os dados do pacote de advertisement
    devices_dict = await BleakScanner.discover(return_adv=True)
    
    for address, (device, adv_data) in devices_dict.items():
        # Filtro por Nome local ou Nome anunciado
        if adv_data.local_name == target_name or device.name == target_name:
            print(f"Dispositivo encontrado por Nome! Endereço atual: {address}")
            return device
            
        # Filtro por UUID de serviço (caso o nome esteja oculto)
        if target_service_uuid and target_service_uuid in adv_data.service_uuids:
            print(f"Dispositivo encontrado por Serviço GATT! Endereço atual: {address}")
            return device

    print("Dispositivo não encontrado pelos critérios alternativos.")
    return None


async def testar_invisibilidade_em_conexao():
    print(f"Conectando a {TARGET_ADDRESS}...")
    async with BleakClient(TARGET_ADDRESS) as client:
        if client.is_connected:
            print("Conexão estabelecida com sucesso!")
            print(">>> Mantenha esta janela aberta e faça um scan no nRF Connect do celular agora. <<<")
            # Mantém a conexão ativa por 30 segundos para permitir o teste no smartphone
            await asyncio.sleep(30)
    print("Conexão encerrada.")


async def connect_device(target_address=TARGET_ADDRESS):
    device = await BleakScanner.find_device_by_address(target_address, timeout=10.0)
    if not device:
        logging.error(f"Dispositivo com endereço {target_address} não encontrado.")

    async with BleakClient(device, timeout=22.0) as client:
        logging.info(f"Conectado a {target_address}")

        while client.is_connected:
            print("Conexão ativa...")
            await asyncio.sleep(2.6)


async def get_device_services(target_address=TARGET_ADDRESS):
    device = await BleakScanner.find_device_by_address(target_address, timeout=10.0)
    if not device:
        logging.error(f"Dispositivo com endereço {target_address} não encontrado.")

    async with BleakClient(device, timeout=22.0) as client:
        logging.info(f"Conectado a {target_address}")

        for service in client.services:
            print(f"[Service] {service.uuid}: {service.description}")
