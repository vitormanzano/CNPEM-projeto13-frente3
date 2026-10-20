import asyncio
from bleak import BleakClient
from bleak import BleakScanner

TARGET_ADDRESS="84B49860-9C1B-D2AC-9ABD-3074E2B20F9F"


"""O RSSI deve ficar entre -55 e --78, ou seja, -78 < RSSI < -55"""
async def find_target_address(target_address=TARGET_ADDRESS):
    """Procura um dispositivo Bluetooth BLE pelo endereço (MAC ou UUID).

    Realiza uma varredura nos dispositivos próximos. Caso encontre um
    dispositivo com endereço correspondente ao `target_address`,
    retorna o objeto `BLEDevice`.

    Args:
        target_address (str): Endereço MAC (Linux/Windows) ou UUID (macOS) do dispositivo alvo.

    Returns:
        BLEDevice | None: Objeto do dispositivo se encontrado; caso contrário, None.
    """
    devices = await BleakScanner.discover(
        # return_adv=True,
    )

    for device in devices:
        if device.address == target_address:
            return device

    return None


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
