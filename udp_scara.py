import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import Float64MultiArray
from builtin_interfaces.msg import Duration
import socket
import json
import select

class UdpScara(Node):
    def __init__(self):
        super().__init__('udp_scara')
        self.arm_pub = self.create_publisher(JointTrajectory, '/arm_controller/joint_trajectory', 10)
        self.grip_pub = self.create_publisher(Float64MultiArray, '/gripper_controller/commands', 10)
        
        self.UDP_IP = "0.0.0.0" 
        self.UDP_PORT = 5005
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.UDP_IP, self.UDP_PORT))
        self.sock.setblocking(0)
        
        self.j1, self.j2, self.j3, self.wrist, self.grip = 0.0, 0.0, 0.0, 0.0, 0.0
        
        # --- O TUNING FINO ---
        self.step_rot = 0.04   # Velocidade de giro dos braços
        self.step_lin = 0.005  # Velocidade do sobe e desce (Prismática)
        self.step_grip = 0.05  # Velocidade de fechamento da Garra
        self.deadzone = 0.15   # Ignora o "drift" de controle velho
        
        self.timer = self.create_timer(0.05, self.timer_callback)
        self.get_logger().info(f"📡 Antena UDP TUNADA ligada! Escutando na porta {self.UDP_PORT}...")

    def timer_callback(self):
        data = None
        while True:
            ready = select.select([self.sock], [], [], 0)
            if ready[0]:
                data, addr = self.sock.recvfrom(1024)
            else:
                break
        
        if data:
            try:
                msg = json.loads(data.decode('utf-8'))
                axes = msg.get("axes", [])
                buttons = msg.get("buttons", [])

                # MAPEAMENTO CORRIGIDO PARA O LINUX (Manba One / Xbox nativo):
                # Eixo 0: Analógico Esq (Esquerda/Direita) -> Joint 1
                # Eixo 1: Analógico Esq (Cima/Baixo)       -> Joint 2
                # O Eixo 2 agora costuma ser o Gatilho L2 (LT) no Linux!
                # Eixo 3: Analógico Dir (Esquerda/Direita) -> Rotação do Punho (Wrist)
                # Eixo 4: Analógico Dir (Cima/Baixo)       -> Sobe e Desce (Prismática / Joint 3)
                
                if len(axes) > 0 and abs(axes[0]) > self.deadzone: self.j1 += axes[0] * self.step_rot
                if len(axes) > 1 and abs(axes[1]) > self.deadzone: self.j2 += axes[1] * self.step_rot
                if len(axes) > 3 and abs(axes[3]) > self.deadzone: self.wrist += axes[3] * self.step_rot
                if len(axes) > 4 and abs(axes[4]) > self.deadzone: self.j3 += axes[4] * self.step_lin

                # A MÁGICA DA GARRA SUAVE
                if len(buttons) > 1:
                    if buttons[0] == 1: self.grip += self.step_grip # Segura 'A' para ir fechando
                    if buttons[1] == 1: self.grip -= self.step_grip # Segura 'B' para ir abrindo

                # LIMITES DE SEGURANÇA (Para o robô não se quebrar)
                self.j1 = max(-1.57, min(1.57, self.j1))
                self.j2 = max(-1.57, min(1.57, self.j2))
                self.j3 = max(-0.15, min(0.0, self.j3)) # Prismatic Z (Pode ajustar esse -0.15 se precisar que desça mais)
                self.wrist = max(-1.57, min(1.57, self.wrist))
                self.grip = max(0.0, min(1.0, self.grip)) # Garra trancada entre 0% e 100%

                # Envia para os motores do braço
                traj = JointTrajectory()
                traj.joint_names = ['joint_1', 'joint_2', 'joint_3', 'wrist_joint']
                point = JointTrajectoryPoint()
                point.positions = [self.j1, self.j2, self.j3, self.wrist]
                point.time_from_start = Duration(sec=0, nanosec=100000000) 
                traj.points.append(point)
                self.arm_pub.publish(traj)

                # Envia para o motor da garra
                grip_msg = Float64MultiArray()
                grip_msg.data = [self.grip]
                self.grip_pub.publish(grip_msg)

            except Exception as e:
                pass

def main(args=None):
    rclpy.init(args=args)
    node = UdpScara()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()