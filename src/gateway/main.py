import asyncio
import os
import sys
from pathlib import Path

# Adiciona o diretório da aplicação ao caminho de busca do Python
PASTA_PAI = Path(__file__).resolve().parent.parent
sys.path.append(str(PASTA_PAI))
sys.path.append(str(Path(__file__).resolve().parent))

# Importa a função específica do arquivo scanner.py
from bluetooth.scanner import *
from bleak import BleakScanner, BleakClient

# Configurações do dispositivo alvo para os testes (suporta variáveis de ambiente)
TARGET_ADDRESS = os.getenv("TARGET_ADDRESS", "F1142908-CB92-D7C9-C4E4-03C134ADB6A7")  # MAC (Linux) ou UUID (macOS)
TARGET_NAME = os.getenv("TARGET_NAME", "Polar Verity")                                # Nome do dispositivo
TARGET_SERVICE_UUID = os.getenv("TARGET_SERVICE_UUID", "F1142908-CB92-D7C9-C4E4-03C134ADB6A7")  # Exemplo: Heart Rate Service


async def teste_1_scan_simples() -> None:
    """TESTE 1: Varredura geral de dispositivos próximos.

    Utilizado para validar a presença do dispositivo e conferir se o endereço
    permanece constante entre reinicializações.
    """
    print("\n" + "=" * 60)
    print("TESTE 1: Scan Simples (Verificação de Endereço/MAC)")
    print("=" * 60)
    print("Iniciando varredura por 5 segundos...\n")

    await find_all_local_devices()
     

async def teste_2_busca_alternativa(
    target_name: str = TARGET_NAME, target_uuid: str = TARGET_SERVICE_UUID
) -> None:
    """TESTE 2: Busca por dados de Advertising (Nome e Serviços).

    Utilizado caso o dispositivo altere o endereço MAC periodicamente (RPA),
    permitindo filtrá-lo por critérios alternativos.
    """
    print("\n" + "=" * 60)
    print("TESTE 2: Busca por Critérios Alternativos (Nome / Serviço)")
    print("=" * 60)
    print(f"Procurando por Nome: '{target_name}' ou UUID: '{target_uuid}'...\n")

    # Retorna o dicionário com dados detalhados do pacote de anúncio
    devices_dict = await BleakScanner.discover(return_adv=True, timeout=5.0)
    encontrado = False

    for address, (device, adv_data) in devices_dict.items():
        match_nome = (adv_data.local_name == target_name) or (device.name == target_name)
        match_uuid = bool(
            target_uuid
            and any(target_uuid.lower() == u.lower() for u in adv_data.service_uuids)
        )

        if match_nome or match_uuid:
            encontrado = True
            print(">>> Dispositivo Alvo Encontrado! <<<")
            print(f"  - Endereço/UUID Atual : {address}")
            print(f"  - Nome Local Anunciado : {adv_data.local_name or device.name}")
            print(f"  - Sinal (RSSI)         : {adv_data.rssi} dBm")
            print(f"  - UUIDs de Serviço     : {adv_data.service_uuids}")
            print(f"  - Dados do Fabricante  : {adv_data.manufacturer_data}")
            break

    if not encontrado:
        print("Dispositivo não localizado pelos critérios alternativos especificados.")


async def teste_3_conexao_e_visibilidade(
    address: str = TARGET_ADDRESS, tempo_permanencia: int = 20
) -> None:
    """TESTE 3: Teste de Conexão GATT e Visibilidade Concorrente.

    Conecta-se ao dispositivo e mantém a sessão aberta para que você valide
    se o dispositivo fica 'invisível' em um scan paralelo (ex.: nRF Connect).
    """
    print("\n" + "=" * 60)
    print("TESTE 3: Conexão e Teste de Visibilidade (1:1)")
    print("=" * 60)
    print(f"Tentando estabelecer conexão com: {address}...\n")

    try:
        async with BleakClient(address, timeout=10.0) as client:
            if client.is_connected:
                print(" Conexão estabelecida com sucesso!")
                print(
                    f"\n>>> Mantenha esta janela aberta e faça um scan no aplicativo nRF Connect agora."
                )
                print(f">>> A conexão permanecerá ativa por {tempo_permanencia} segundos...\n")

                for tempo_restante in range(tempo_permanencia, 0, -5):
                    print(f"Conexão ativa. Tempo restante: {tempo_restante}s...")
                    await asyncio.sleep(5)

                print("\nEncerrando sessão de conexão...")
    except Exception as erro:
        print(f" Falha ao conectar ao dispositivo {address}: {erro}")


async def main() -> None:
    await connect_and_monitor_rssi("F1142908-CB92-D7C9-C4E4-03C134ADB6A7")
    # await find_all_local_devices()  
    # await connect_device("F1142908-CB92-D7C9-C4E4-03C134ADB6A7")

    # """Menu interativo para execução dos testes."""
    # while True:
    #     print("\n" + "#" * 50)
    #     print("      SUÍTE DE TESTES BLE - DIAGNÓSTICO FRENTE 3")
    #     print("#" * 50)
    #     print("1. Executar Teste 1: Scan Simples (Verificar MAC/UUIDs)")
    #     print("2. Executar Teste 2: Filtrar por Nome/Serviço (Critérios Alternativos)")
    #     print("3. Executar Teste 3: Testar Conexão GATT e Visibilidade no celular")
    #     print("4. Executar TODOS os testes em sequência")
    #     print("0. Sair")
    #
    #     opcao = input("\nSelecione uma opção (0-4): ").strip()
    #
    #     if opcao == "1":
    #         await teste_1_scan_simples()
    #     elif opcao == "2":
    #         await teste_2_busca_alternativa()
    #     elif opcao == "3":
    #         await teste_3_conexao_e_visibilidade()
    #     elif opcao == "4":
    #         await teste_1_scan_simples()
    #         await teste_2_busca_alternativa()
    #         await teste_3_conexao_e_visibilidade()
    #     elif opcao == "0":
    #         print("\nSaindo do programa de testes.")
    #         break
    #     else:
    #         print("\nOpção inválida. Digite um número de 0 a 4.")


if __name__ == "__main__":
    asyncio.run(main())
