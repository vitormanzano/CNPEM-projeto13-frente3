#!/bin/bash

# Encerra o script se algum comando falhar
set -e

# --- Docker --- 

echo "Atualizando pacotes e instalando dependências iniciais..."
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

echo "Desinstalando pacotes antigos que podem dar conflito"
sudo apt remove $(dpkg --get-selections docker.io docker-compose docker-compose-v2 docker-doc docker-buildx podman-docker containerd runc | cut -f1)

echo "Adicionando a chave GPG oficial do Docker..."
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "Configurando o repositório oficial do Docker..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "Atualizando a lista de pacotes com o novo repositório..."
sudo apt-get update

echo "Instalando o Docker Engine e plugins (incluindo Docker Compose)..."
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "Iniciando e habilitando o serviço do Docker..."
sudo systemctl start docker

echo "Adicionando o usuário $USER ao grupo 'docker'..."
sudo usermod -aG docker $USER

echo "Instalação concluída com sucesso!"
echo "ATENÇÃO: É necessário fazer logout e login novamente para aplicar as permissões do grupo docker."
# --- Fim Docker --- 
