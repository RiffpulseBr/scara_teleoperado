# 🤖 SCARA Teleoperado - ROS 2 & Gazebo

Projeto final de simulação de um robô manipulador SCARA com controle em tempo real via joystick. A comunicação entre o hardware de controle e os nós do simulador é feita de forma descentralizada através de telemetria UDP, permitindo a separação entre a estação de controle e a planta simulada.

## 🛠️ Tecnologias Utilizadas
* **Sistema Operacional:** Ubuntu 22.04 LTS
* **Framework de Robótica:** ROS 2 (Humble)
* **Middleware de Rede:** Eclipse Cyclone DDS
* **Simulador:** Gazebo
* **Linguagens e Bibliotecas:** Python 3, `rclpy`, `pygame`, `socket`
* **Hardware de Interface:** Controle Manba One (ou padrão Xbox 360)

## ⚙️ Configuração do Ambiente (Máquina Virtual)

Caso o sistema esteja rodando através de virtualização (VirtualBox), é mandatório configurar o Passthrough do USB para evitar que o sistema operacional hospedeiro bloqueie os pacotes de dados do controle:

1. Com a VM desligada, acesse **Configurações > USB**.
2. Selecione a controladora **USB 2.0 (EHCI)** ou **3.0 (xHCI)**.
3. Conecte o joystick no PC físico, adicione-o na lista de Filtros (ícone de `+`) e salve.
4. **Desconecte o controle do PC físico**.
5. Ligue a Máquina Virtual e aguarde o Ubuntu carregar completamente a interface gráfica.
6. Só então, reconecte o controle na porta USB.

---

## 🚀 Como Executar o Sistema

A arquitetura do projeto exige a inicialização sequencial de 4 terminais independentes. Abra as abas no terminal e execute os passos abaixo rigorosamente na ordem:

### Aba 1: Ambiente de Simulação (Gazebo)
Garante as regras de isolamento de rede e lança o mundo físico.
```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_LOCALHOST_ONLY=1
source ~/scara_ws/install/setup.bash
ros2 launch scara_description gazebo.launch.py
```
*(Aguarde o robô ser renderizado e a mensagem de sucesso no terminal).*

### Aba 2: Controladores e Motores
Injeta as juntas no `controller_manager` do ROS 2.
```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_LOCALHOST_ONLY=1
source ~/scara_ws/install/setup.bash
ros2 launch scara_description controller.launch.py
```
*(Aguarde a ativação confirmada dos 3 painéis de controle).*

### Aba 3: Nó Receptor UDP (Cérebro)
Fica em estado de escuta (`listen`) aguardando os pacotes da estação de operação.
```bash
export ROS_LOCALHOST_ONLY=1
source ~/scara_ws/install/setup.bash
python3 ~/scara_ws/udp_scara.py
```

### Aba 4: Estação de Transmissão (Piloto)
Captura os dados de hardware via `evdev`/Pygame e transmite pela rede local (Porta 5005).
```bash
python3 ~/scara_ws/transmissor_controle.py
```
> ⚠️ **Atenção:** Mantenha a interface gráfica preta do Painel SCARA (Pygame) **em foco** para que o sistema operacional autorize a captura dos analógicos.

---

## 🎮 Mapeamento de Eixos
Mapeamento adaptado para o subsistema de eventos do Linux nativo:

* **Analógico Esquerdo (Eixo X):** Rotação da Junta 1 (Base)
* **Analógico Esquerdo (Eixo Y):** Rotação da Junta 2 (Braço Intermediário)
* **Analógico Direito (Eixo X):** Rotação do Punho (Orientação da Garra)
* **Analógico Direito (Eixo Y):** Junta Prismática (Eixo Z - Sobe/Desce)
* **Botão A:** Acionamento positivo (Fechar Garra)
* **Botão B:** Acionamento negativo (Abrir Garra)
