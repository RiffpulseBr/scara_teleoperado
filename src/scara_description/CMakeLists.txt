cmake_minimum_required(VERSION 3.8)
project(scara_description)

find_package(ament_cmake REQUIRED)

# Instala todos os diretórios de recursos para o share do pacote.
# O colcon vai copiar esses arquivos para o install/, onde o
# robot_state_publisher vai encontrá-los via ament_index.
install(
  DIRECTORY
    urdf
    meshes
    launch
    rviz
    config
  DESTINATION share/${PROJECT_NAME}
)

install(
  DIRECTORY config launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
