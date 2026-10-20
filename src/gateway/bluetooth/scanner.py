import asyncio
from bleak import BleakClient
from bleak.exc import BleakError
import traceback
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
            print("ACHOU")
            return device

    return None


async def find_all_local_devices():
    devices_dict = await BleakScanner.discover(return_adv=True, timeout=5.0)

    if not devices_dict:
        print("Nenhum dispositivo BLE encontrado ao alcance.")
        return

    for address, (dev, adv_data) in devices_dict.items():
        nome = dev.name or adv_data.local_name or "Desconhecido / Oculto"
        rssi = adv_data.rssi  
        print(f"Endereço: {address} | Nome: {nome:<25} | RSSI: {rssi} dBm")

    return devices_dict


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
    print(f"Procurando dispositivo {target_address}...")
    device = await find_target_address(target_address)

    if device is None:
        print("Dispositivo não encontrado no scan inicial. Verifique se ele está ligado e anunciando.")
        return

    print(f"Dispositivo encontrado ({device.name or 'Sem Nome'}). Tentando conectar...")

    try:
        # Passa o objeto 'device' diretamente para evitar que o Bleak faça um novo scan
        async with BleakClient(device, timeout=15.0) as client:
            print("Conectado com sucesso!", client.is_connected)

            while client.is_connected:
                await get_current_rssi(client)

    except BleakError as e:
        # Exibe a classe exata da exceção Bleak e seu valor interno
        print(f"Falha de conexão Bleak [{type(e).__name__}]: {repr(e)}")

    except Exception as e:
        # Exibe o tipo de erro genérico e imprime o rastreamento completo no terminal
        print(f"\n[ERRO Capturado] Tipo: {type(e).__name__}")
        print(f"Detalhes do erro: {repr(e)}")
        print("\n--- Rastreamento Completo da Falha (Stack Trace) ---")
        traceback.print_exc()

async def get_current_rssi(client, seconds_interval: float = 1.0):
    rssi = await client.get_rssi()
    print(f"RSSI Atual: {rssi} dBm")

    await asyncio.sleep(seconds_interval)


async def connect_and_monitor_rssi(address: str = TARGET_ADDRESS):
    print(f"Buscando dispositivo ativo no macOS: {address}...")

    # Localiza o dispositivo em tempo real sem usar objetos em cache
    device = await BleakScanner.find_device_by_address(address, timeout=10.0)

    if device is None:
        print("❌ Dispositivo não localizado no scan. Certifique-se de que ele está ligado e anunciando.")
        return

    print(f"✅ Dispositivo encontrado ({device.name or 'Sem Nome'}). Tentando conectar...")

    try:
        # Aumente o timeout para 20.0s para dar tempo ao CoreBluetooth do macOS
        async with BleakClient(device, timeout=20.0) as client:
            print(f"🔗 Conectado com sucesso! Status: {client.is_connected}")

            while client.is_connected:
                rssi = await client.get_rssi()
                print(f"📡 RSSI Atual: {rssi} dBm")
                await asyncio.sleep(1.0)

    except asyncio.TimeoutError:
        print("\n❌ [TimeoutError] A pilha CoreBluetooth do macOS não respondeu a tempo.")
        print("Verificações recomendadas:")
        print(" 1. Desconecte o dispositivo do Bluetooth do celular ou de outros apps.")
        print(" 2. Remova o dispositivo do menu 'Ajustes do Sistema > Bluetooth' do macOS (se estiver pareado).")
        print(" 3. Verifique as permissões de privacidade do Terminal/IDE no macOS.")

    except BleakError as e:
        print(f"❌ Erro da biblioteca Bleak: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado [{type(e).__name__}]: {e}")
        traceback.print_exc()
