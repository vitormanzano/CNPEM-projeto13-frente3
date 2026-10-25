# Linguagem ubíqua
É uma linguagem comum e rigorosa compartilhada entre todas as pessoas envolvidas no projeto. Tendo benefícios como:
- Elimina ambiguidade: Todos usam exatamente as mesmas palavras para descrever os conceitos do sistema.
- Conecta o negócio com o código: Os termos do vocabulário aparecem no sistema.

## Termos (Português)
- Pesquisadores: Pessoas que utilizarão a pulseira.
- Pulseira: Pulseira Polar que será usada pelos pesquisadores do laboratório para monitorar sinais vitais.
- Coletor BLE: Dispositivo Raspberry PI que será utilizado para se conectar com a pulseira.
- Broker: Servidor MQTT (HiveMQ) que recebe as mensagens dos coletores e as distribui.
- Handoff: Transferência da conexão de uma pulseira de um coletor para outro.
- RSSI: Intensidade do sinal entre um coletor e uma pulseira, em dBm.
- Estado da conexão: conectado | desconectado | conexao-fraca | nao-encontrado.
