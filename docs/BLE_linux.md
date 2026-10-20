# Como funciona a conexão bluetooth no Linux?

## Hardware
O hardware físico, representado por uma placa Raspberry PI. Existe o chip/adaptador de rádio bluetooth. O pápel do hardware é transmitir e receber ondas eletromagnéticas (pacotes de dados) pelo ar.

## Camada de Sistema Operacional (Bluez)
O Bluez é conectado diretamente ao hardware. É o serviço oficial do kernel do Linux, responsável por gerenciar a pilha bluetooth. Ele atua como um driver lógico, traduzindo os sinais de rádio do hardware físico
em protocolos estruturados e vice-versa.

## Camada de Mensageria (D-Bus)
D-Bus é um serviço de sistema e um tipo de middleware orientado a mensagens que provê suporte à ICP para aplicações Linux. 
Para que os programas não tentem acessar o hardware Bluetooth ao mesmo tempo e causem conflitos, o Bluez expõe suas funcionalidades no D-Bus
através de um socket específico localizado em `/var/run/dbus`.

## Camada de Aplicação (Código)
Para interagir com o Bluetooth, o meu código se conecta ao mesmo socket /var/run/dbus. 
Esse é o pápel do Bleak, ele usa clientes D-Bus em Python para injetar e ler informações nesse canal sem terminais ou comandos.

![Arquitetura do Bluetooth no Linux](./images/linux-bluetooth-architecture.jpg)

### Referência
https://www.bluetooth.com/blog/the-bluetooth-for-linux-developers-study-guide/
