# practica-docker-compose
Aplicacion Hola Mundo conectada a MySQL con Docker Compose

## Practica: Ansible + Docker Compose (5 servidores Ubuntu)

Archivos: `Dockerfile` (Ubuntu + sshd, usuario `ansible`/`ansible` con sudo sin password), `docker-compose.yml` (5 servicios), `inventario.ini`, `ansible.cfg`, `playbook.yml`.

### 1. Levantar los servidores
```bash
docker compose up -d --build
```
Red `172.30.0.0/24`: servidor1..5 = `172.30.0.11`..`172.30.0.15`. Cada SSH se publica en `127.0.0.1:2221`..`2225`.

### 2. Instalar Ansible (Windows: `wsl --install`, luego en Ubuntu)
```bash
sudo apt update && sudo apt install -y ansible sshpass
```
`sshpass` es necesario para autenticar con password.

### 3. Inventario y configuracion
El inventario usa `127.0.0.1` con el puerto publicado de cada servidor, porque las IPs internas de Docker (172.30.0.x) no son accesibles desde WSL/host con Docker Desktop. Las IPs internas se anotan como `ip_interna`. `ansible.cfg` apunta a `inventario.ini` y desactiva la advertencia de host key SSH.

### 4. Ejecutar
Desde la carpeta del repo (mejor clonado dentro del filesystem de WSL; en `/mnt/c` Ansible ignora `ansible.cfg` por ser carpeta world-writable, y deberas usar `export ANSIBLE_CONFIG=$PWD/ansible.cfg`):
```bash
ansible all -m ping
ansible-playbook playbook.yml
```
El playbook: actualiza APT, crea el usuario `itla`, crea `/home/itla/app`, crea `hola.txt` e instala `cowsay` y `htop`. Es idempotente.

### 5. Verificar
```bash
ansible all -a "cat /home/itla/app/hola.txt"
ansible all -a "/usr/games/cowsay Hola"
ansible all -a "which htop"
```

Repositorio: https://github.com/juliorijo/practica-docker-compose
