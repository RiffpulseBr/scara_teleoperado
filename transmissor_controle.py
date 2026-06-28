import pygame
import socket
import json
import time

# Configuração da Rede Interna da VM
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

pygame.init()
pygame.joystick.init()

quantidade_controles = pygame.joystick.get_count()

if quantidade_controles == 0:
    print("❌ ERRO: O Pygame não inicializou nenhum controle!")
    print("Execute no terminal: sudo chmod 666 /dev/input/js*")
    exit()

# Varre os índices para achar o controle ativo (resolve o problema do js1)
joystick = None
for i in range(quantidade_controles):
    try:
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        print(f"🎮 Controle conectado com sucesso no índice [{i}]: {joystick.get_name()}")
        break
    except Exception:
        continue

if not joystick:
    print("❌ ERRO: Falha ao inicializar o hardware do controle.")
    exit()

# Cria a janela nativa do Ubuntu necessária para capturar os eventos
screen = pygame.display.set_mode((400, 100))
pygame.display.set_caption("🎮 Painel SCARA (Mantenha em Foco)")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("📡 Transmitindo dados locais via UDP para o SCARA...")

try:
    while True:
        pygame.event.pump()
        
        # Captura os estados reais de eixos e botões
        axes = [joystick.get_axis(j) for j in range(joystick.get_numaxes())]
        buttons = [joystick.get_button(j) for j in range(joystick.get_numbuttons())]

        # Monta a telemetria em JSON
        pacote = {"axes": axes, "buttons": buttons}
        sock.sendto(json.dumps(pacote).encode('utf-8'), (UDP_IP, UDP_PORT))
        
        time.sleep(0.05) # Taxa industrial de atualização (20Hz)

except KeyboardInterrupt:
    print("\nDesligando sistema de transmissão...")
finally:
    pygame.quit()