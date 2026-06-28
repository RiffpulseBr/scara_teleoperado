# scara_description

Pacote ROS 2 (Humble) de descrição URDF/Xacro do manipulador SCARA.  
Configurado para o **workflow de ajuste visual empírico**: você edita variáveis
no `.xacro` e recarrega sem fechar o RViz.

---

## Estrutura do pacote

```
scara_description/
├── CMakeLists.txt
├── package.xml
├── urdf/
│   └── scara.urdf.xacro        ← EDITE AQUI (variáveis *_v_*)
├── meshes/
│   ├── bs.stl                  ← copie seus STLs aqui
│   ├── es.stl
│   ├── as.stl
│   ├── cs.stl
│   ├── g1.stl
│   ├── g2.stl
│   └── g3.stl
├── launch/
│   └── display.launch.py
├── rviz/
│   └── scara.rviz
└── config/
    └── reload_urdf.sh          ← atalho de recarga em tempo real
```

---

## Instalação e primeiro build

```bash
# 1. Coloque seus arquivos .stl em meshes/
cp /caminho/dos/seus/stls/*.stl ~/scara_ws/src/scara_description/meshes/

# 2. Build (só precisa rodar uma vez, ou após mudar CMakeLists/package.xml)
cd ~/scara_ws
colcon build --packages-select scara_description

# 3. Source (rode em TODO terminal novo que for usar)
source ~/scara_ws/install/setup.bash
```

---

## Workflow de ajuste visual (loop principal)

### Terminal 1 — sobe o RViz (deixe aberto)
```bash
source ~/scara_ws/install/setup.bash
ros2 launch scara_description display.launch.py
```
O RViz abre com:
- **Grid** no chão (referência Z=0)
- **RobotModel** (as malhas coloridas)
- **TF** com nomes visíveis (os frames = o "esqueleto")

### Terminal 2 — loop de edição e recarga
```bash
source ~/scara_ws/install/setup.bash

# Edite as variáveis visuais no xacro:
nano ~/scara_ws/src/scara_description/urdf/scara.urdf.xacro

# Recarregue SEM fechar o RViz:
bash ~/scara_ws/src/scara_description/config/reload_urdf.sh
```

> **Importante:** O `reload_urdf.sh` lê o arquivo de `install/`.  
> Se você editar o arquivo em `src/` (o correto), precisa rodar  
> `colcon build --packages-select scara_description` **uma vez** depois  
> de cada ciclo de ajuste, ou usar um symlink (veja abaixo).

### Alternativa: symlink para editar sem rebuild
```bash
# Faz o install/ apontar para o src/ diretamente
colcon build --packages-select scara_description --symlink-install

# A partir daí, qualquer edição em src/urdf/scara.urdf.xacro
# é refletida IMEDIATAMENTE ao rodar reload_urdf.sh — sem rebuild!
```

---

## O que ajustar no xacro

Abra `urdf/scara.urdf.xacro` e procure a **SEÇÃO 2**.  
São as únicas variáveis que você deve mexer durante o ajuste visual:

```xml
<!-- Exemplo: ombro está 9 cm para a esquerda e 4.5 cm acima do frame -->
<xacro:property name="es_v_x"   value="-0.090"/>
<xacro:property name="es_v_y"   value="0.0"/>
<xacro:property name="es_v_z"   value="-0.045"/>
```

### Ordem de ajuste recomendada (de baixo pra cima)

| Passo | Link       | Frame de referência TF | Variáveis         |
|-------|------------|------------------------|-------------------|
| 1     | base_link  | `base_link` (origem)   | `bs_v_x/y/z`      |
| 2     | es_link    | `joint_1`              | `es_v_x/y/z`      |
| 3     | as_link    | `joint_2`              | `as_v_x/y/z`      |
| 4     | cs_link    | `joint_3`              | `cs_v_x/y/z`      |
| 5     | g1_gripper | `wrist_joint`          | `g1_v_x/y/z`      |
| 6     | g2/g3      | `gripper_joint1/2`     | `g2_v_*`/`g3_v_*` |

**Dica de sinal:** a malha está 5 cm à direita do frame? Use `v_x = -0.05`  
(você move a malha, não o frame).

---

## Verificação rápida do URDF

```bash
# Checa erros de sintaxe sem abrir o RViz
check_urdf <(xacro ~/scara_ws/src/scara_description/urdf/scara.urdf.xacro)

# Imprime a árvore de links no terminal
urdf_to_graphviz <(xacro scara.urdf.xacro) && evince scara.pdf
```
