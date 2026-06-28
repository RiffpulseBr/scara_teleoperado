#!/usr/bin/env bash
# =============================================================================
# reload_urdf.sh — Recarrega o xacro em tempo real SEM fechar o RViz.
#
# Como usar:
#   1. Deixe o RViz aberto (via display.launch.py).
#   2. Edite as variáveis es_v_x, bs_v_z etc. no scara.urdf.xacro.
#   3. Rode este script em outro terminal:
#        bash reload_urdf.sh
#   4. O RViz atualiza automaticamente (usa o tópico /robot_description).
#
# Pré-requisito: source do workspace feito no terminal atual.
#   source ~/scara_ws/install/setup.bash
# =============================================================================

set -e

PACKAGE="scara_description"
XACRO_FILE="$(ros2 pkg prefix $PACKAGE)/share/$PACKAGE/urdf/scara.urdf.xacro"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Recarregando: $XACRO_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Processa o xacro e injeta via parâmetro ROS 2
URDF=$(xacro "$XACRO_FILE")

ros2 param set /robot_state_publisher robot_description "$URDF"

echo "✓ robot_description atualizado. Confira o RViz."
