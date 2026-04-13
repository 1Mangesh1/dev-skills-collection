---
name: ansible
description: Ansible automation for server configuration, deployment, and infrastructure management. Use when user mentions "ansible", "ansible-playbook", "ansible-vault", "inventory", "playbook", "ansible role", "ansible galaxy", "configuration management", "server provisioning", "infrastructure automation", "ansible task", "ansible template", or automating server setup and deployment.
---

# Ansible

Agentless automation over SSH. No agents to install on managed nodes -- just Python on targets and SSH access. All modules are idempotent by default: running a playbook twice produces the same result.

## Ad-Hoc Commands

```bash
# Ping all hosts
ansible all -m ping

# Run command on web servers
ansible webservers -m command -a "uptime"
ansible webservers -m shell -a "df -h | grep /dev/sda"

# Copy file
ansible webservers -m copy -a "src=./app.conf dest=/etc/app.conf owner=root mode=0644"

# Install package
ansible webservers -m apt -a "name=nginx state=present" --become

# Manage service
ansible webservers -m systemd -a "name=nginx state=restarted enabled=yes" --become

# Create user
ansible all -m user -a "name=deploy shell=/bin/bash groups=sudo" --become

# Gather facts
ansible webservers -m setup -a "filter=ansible_distribution*"
```

## Inventory

### Static Inventory (hosts.ini)

```ini
[webservers]
web1.example.com ansible_host=10.0.1.10
web2.example.com ansible_host=10.0.1.11

[dbservers]
db1.example.com ansible_host=10.0.2.10 ansible_port=2222

[production:children]
webservers
dbservers

[webservers:vars]
ansible_user=deploy
ansible_python_interpreter=/usr/bin/python3

[all:vars]
ansible_ssh_private_key_file=~/.ssh/deploy_key
```

### YAML Inventory (inventory.yml)

```yaml
all:
  children:
    webservers:
      hosts:
        web1.example.com:
          ansible_host: 10.0.1.10
          http_port: 8080
        web2.example.com:
          ansible_host: 10.0.1.11
    dbservers:
      hosts:
        db1.example.com:
          ansible_host: 10.0.2.10
      vars:
        db_port: 5432
```

### Host and Group Variables

```
inventory/
  hosts.yml
  group_vars/
    all.yml            # Applies to every host
    webservers.yml     # Applies to webservers group
    production.yml
  host_vars/
    web1.example.com.yml
```

### Dynamic Inventory

```bash
# AWS EC2
ansible-inventory -i aws_ec2.yml --list

# Plugin config (aws_ec2.yml)
```

```yaml
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1
filters:
  tag:Environment: production
keyed_groups:
  - key: tags.Role
    prefix: role
compose:
  ansible_host: private_ip_address
```

## Playbook Structure

```yaml
---
- name: Configure web servers
  hosts: webservers
  become: yes
  vars:
    app_port: 8080
    app_user: www-data

  pre_tasks:
    - name: Update apt cache
      apt:
        update_cache: yes
        cache_valid_time: 3600

  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: present

    - name: Deploy nginx config
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/sites-available/default
        owner: root
        mode: "0644"
      notify: Restart nginx

    - name: Ensure nginx is running
      systemd:
        name: nginx
        state: started
        enabled: yes

  handlers:
    - name: Restart nginx
      systemd:
        name: nginx
        state: restarted

  post_tasks:
    - name: Verify nginx is responding
      uri:
        url: "http://localhost:{{ app_port }}"
        status_code: 200
```

```bash
# Run playbook
ansible-playbook site.yml
ansible-playbook site.yml -i inventory/hosts.yml
ansible-playbook site.yml --limit webservers
ansible-playbook site.yml --check          # Dry run
ansible-playbook site.yml --diff           # Show file changes
ansible-playbook site.yml -e "app_port=9090"
ansible-playbook site.yml --start-at-task="Deploy nginx config"
```

## Common Modules

```yaml
# Package management
- apt:
    name: [nginx, curl, git]
    state: present
- yum:
    name: httpd
    state: latest

# Files and directories
- file:
    path: /opt/app
    state: directory
    owner: deploy
    group: deploy
    mode: "0755"
- file:
    path: /tmp/old_file
    state: absent

# Copy files
- copy:
    src: files/app.conf
    dest: /etc/app/app.conf
    owner: root
    mode: "0644"
    backup: yes
- copy:
    content: "{{ lookup('template', 'config.j2') }}"
    dest: /etc/app/config.yml

# Templates
- template:
    src: templates/vhost.conf.j2
    dest: /etc/nginx/conf.d/app.conf
    validate: "nginx -t -c %s"

# Services
- systemd:
    name: nginx
    state: restarted
    daemon_reload: yes
    enabled: yes

# Users and groups
- user:
    name: deploy
    shell: /bin/bash
    groups: [sudo, docker]
    append: yes
    generate_ssh_key: yes
- authorized_key:
    user: deploy
    key: "{{ lookup('file', 'files/deploy.pub') }}"

# Git checkout
- git:
    repo: https://github.com/org/app.git
    dest: /opt/app
    version: main
    force: yes

# Docker containers
- docker_container:
    name: redis
    image: redis:7-alpine
    state: started
    restart_policy: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

# Download files
- get_url:
    url: https://example.com/app.tar.gz
    dest: /tmp/app.tar.gz
    checksum: sha256:abcdef1234567890

# Run commands
- command: /opt/app/migrate.sh
  args:
    chdir: /opt/app
    creates: /opt/app/.migrated
- shell: cat /etc/passwd | grep deploy
  register: deploy_check
  changed_when: false

# Cron jobs
- cron:
    name: "Daily backup"
    minute: "0"
    hour: "2"
    job: "/opt/scripts/backup.sh >> /var/log/backup.log 2>&1"
```

## Variables and Facts

```yaml
# Variable precedence (lowest to highest):
# role defaults -> inventory vars -> playbook vars -> role vars
# -> include_vars -> set_fact -> extra vars (-e)

# Register output
- command: whoami
  register: current_user
- debug:
    msg: "Running as {{ current_user.stdout }}"

# Set facts dynamically
- set_fact:
    app_version: "{{ lookup('file', 'VERSION') }}"
    deploy_timestamp: "{{ ansible_date_time.iso8601 }}"

# Access facts
- debug:
    msg: "OS: {{ ansible_distribution }} {{ ansible_distribution_version }}"
- debug:
    msg: "IP: {{ ansible_default_ipv4.address }}"
- debug:
    msg: "Memory: {{ ansible_memtotal_mb }} MB"

# Include vars from file
- include_vars:
    file: "{{ ansible_distribution | lower }}.yml"
```

## Jinja2 Templates

```jinja2
{# templates/nginx.conf.j2 #}
server {
    listen {{ http_port | default(80) }};
    server_name {{ server_name }};

    {% if ssl_enabled | default(false) %}
    listen 443 ssl;
    ssl_certificate     /etc/ssl/certs/{{ domain }}.crt;
    ssl_certificate_key /etc/ssl/private/{{ domain }}.key;
    {% endif %}

    {% for location in app_locations %}
    location {{ location.path }} {
        proxy_pass http://{{ location.upstream }};
    }
    {% endfor %}

    access_log /var/log/nginx/{{ server_name }}_access.log;
}
```

Common Jinja2 filters:

```yaml
# Defaults
"{{ variable | default('fallback') }}"

# String
"{{ name | upper }}"
"{{ name | lower }}"
"{{ path | basename }}"
"{{ path | dirname }}"

# Lists
"{{ packages | join(', ') }}"
"{{ users | map(attribute='name') | list }}"
"{{ items | unique | sort }}"

# Data
"{{ dict_var | to_json }}"
"{{ dict_var | to_yaml }}"
"{{ 'password' | password_hash('sha512') }}"

# Ternary
"{{ 'yes' if enabled else 'no' }}"
```

## Conditionals and Loops

```yaml
# When conditional
- apt:
    name: nginx
  when: ansible_distribution == "Ubuntu"

- yum:
    name: httpd
  when: ansible_os_family == "RedHat"

- service:
    name: app
    state: restarted
  when: deploy_result is changed

- debug:
    msg: "Low disk"
  when: ansible_mounts | selectattr('mount', 'equalto', '/') | map(attribute='size_available') | first < 1073741824

# Loops
- user:
    name: "{{ item }}"
    state: present
  loop:
    - alice
    - bob
    - carol

- apt:
    name: "{{ item.name }}"
    state: "{{ item.state }}"
  loop:
    - { name: nginx, state: present }
    - { name: apache2, state: absent }

# Loop with index
- debug:
    msg: "{{ index }}: {{ item }}"
  loop: "{{ users }}"
  loop_control:
    index_var: index
    label: "{{ item.name }}"

# Until retry loop
- uri:
    url: http://localhost:8080/health
    status_code: 200
  register: health
  until: health.status == 200
  retries: 30
  delay: 5
```

## Error Handling

```yaml
# Ignore errors
- command: /opt/app/check.sh
  ignore_errors: yes
  register: check_result

# Custom failure condition
- command: /opt/app/status.sh
  register: status
  failed_when: "'ERROR' in status.stdout"
  changed_when: "'UPDATED' in status.stdout"

# Block / rescue / always (try/catch/finally)
- block:
    - name: Deploy application
      git:
        repo: https://github.com/org/app.git
        dest: /opt/app
        version: "{{ app_version }}"
    - name: Run migrations
      command: ./migrate.sh
      args:
        chdir: /opt/app
  rescue:
    - name: Rollback on failure
      command: ./rollback.sh
      args:
        chdir: /opt/app
    - name: Send failure alert
      mail:
        to: ops@example.com
        subject: "Deploy failed on {{ inventory_hostname }}"
        body: "Rolled back to previous version."
  always:
    - name: Restart application
      systemd:
        name: app
        state: restarted
```

## Tags

```yaml
- name: Install packages
  apt:
    name: nginx
  tags: [packages, nginx]

- name: Configure nginx
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
  tags: [config, nginx]

- name: Deploy application
  git:
    repo: https://github.com/org/app.git
    dest: /opt/app
  tags: [deploy]
```

```bash
ansible-playbook site.yml --tags "deploy"
ansible-playbook site.yml --skip-tags "packages"
ansible-playbook site.yml --tags "config,nginx"
ansible-playbook site.yml --list-tags
```

## Roles

### Directory Structure

```
roles/
  webserver/
    defaults/main.yml      # Default variables (lowest precedence)
    vars/main.yml          # Role variables (high precedence)
    tasks/main.yml         # Task list
    handlers/main.yml      # Handlers
    templates/             # Jinja2 templates
    files/                 # Static files
    meta/main.yml          # Role metadata and dependencies
```

### Example Role

```yaml
# roles/webserver/defaults/main.yml
http_port: 80
server_name: localhost
document_root: /var/www/html

# roles/webserver/tasks/main.yml
---
- name: Install nginx
  apt:
    name: nginx
    state: present

- name: Deploy config
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/sites-available/default
  notify: Reload nginx

- name: Enable site
  file:
    src: /etc/nginx/sites-available/default
    dest: /etc/nginx/sites-enabled/default
    state: link

# roles/webserver/handlers/main.yml
---
- name: Reload nginx
  systemd:
    name: nginx
    state: reloaded

# roles/webserver/meta/main.yml
---
dependencies:
  - role: common
  - role: firewall
    vars:
      open_ports: [80, 443]
```

```yaml
# Use role in playbook
- hosts: webservers
  become: yes
  roles:
    - common
    - { role: webserver, http_port: 8080 }
    - role: ssl
      when: ssl_enabled | default(false)
```

## Ansible Galaxy

```bash
# Install roles
ansible-galaxy install geerlingguy.docker
ansible-galaxy install -r requirements.yml

# Install collections
ansible-galaxy collection install community.docker
ansible-galaxy collection install -r requirements.yml

# Initialize new role
ansible-galaxy role init my_role

# List installed
ansible-galaxy list
ansible-galaxy collection list
```

```yaml
# requirements.yml
roles:
  - name: geerlingguy.docker
    version: "6.1.0"
  - name: geerlingguy.certbot
  - src: https://github.com/org/custom-role.git
    name: custom_role
    version: main

collections:
  - name: community.docker
    version: ">=3.0.0"
  - name: amazon.aws
    version: "7.0.0"
```

## Ansible Vault

```bash
# Encrypt a file
ansible-vault encrypt vars/secrets.yml

# Decrypt
ansible-vault decrypt vars/secrets.yml

# Edit encrypted file in-place
ansible-vault edit vars/secrets.yml

# View without decrypting
ansible-vault view vars/secrets.yml

# Change encryption password
ansible-vault rekey vars/secrets.yml

# Encrypt a single string
ansible-vault encrypt_string 'SuperSecret123' --name 'db_password'

# Run playbook with vault
ansible-playbook site.yml --ask-vault-pass
ansible-playbook site.yml --vault-password-file ~/.vault_pass
```

```yaml
# vars/secrets.yml (encrypted content)
db_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  6234613839383...

# ansible.cfg - avoid typing password every time
[defaults]
vault_password_file = ~/.vault_pass
```

## Docker and Container Management

```yaml
# Requires: ansible-galaxy collection install community.docker

- name: Deploy containerized app
  hosts: docker_hosts
  become: yes
  collections:
    - community.docker

  tasks:
    - name: Install Docker
      include_role:
        name: geerlingguy.docker

    - name: Pull image
      docker_image:
        name: myapp
        tag: "{{ app_version }}"
        source: pull

    - name: Run app container
      docker_container:
        name: myapp
        image: "myapp:{{ app_version }}"
        state: started
        restart_policy: unless-stopped
        ports:
          - "8080:8080"
        env:
          DATABASE_URL: "{{ db_url }}"
          REDIS_URL: "{{ redis_url }}"
        volumes:
          - app_data:/data
        networks:
          - name: app_network

    - name: Docker compose deployment
      docker_compose_v2:
        project_src: /opt/app
        state: present
        pull: always
```

## Testing with Molecule

```bash
pip install molecule molecule-docker

# Initialize
cd roles/webserver
molecule init scenario --driver-name docker

# Test lifecycle
molecule create       # Create test instance
molecule converge     # Run role against instance
molecule verify       # Run tests
molecule destroy      # Clean up
molecule test         # Full cycle (create -> converge -> verify -> destroy)
```

```yaml
# molecule/default/molecule.yml
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: ubuntu
    image: ubuntu:22.04
    pre_build_image: false
    command: /sbin/init
    privileged: true
  - name: rocky
    image: rockylinux:9
    command: /sbin/init
    privileged: true
provisioner:
  name: ansible
verifier:
  name: ansible

# molecule/default/verify.yml
---
- name: Verify
  hosts: all
  tasks:
    - name: Check nginx is running
      command: systemctl is-active nginx
      changed_when: false
    - name: Check port 80
      wait_for:
        port: 80
        timeout: 5
```

## Performance Tuning

```ini
# ansible.cfg
[defaults]
forks = 20                          # Parallel host connections (default 5)
gathering = smart                   # Cache facts, don't re-gather
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 86400
host_key_checking = False
stdout_callback = yaml              # Readable output

[ssh_connection]
pipelining = True                   # Reduce SSH operations (requires requiretty off)
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
```

```yaml
# Async tasks for long operations
- name: Long running update
  apt:
    upgrade: dist
  async: 3600       # Max runtime in seconds
  poll: 10          # Check every 10 seconds (0 = fire and forget)

# Limit fact gathering
- hosts: webservers
  gather_facts: no
  tasks:
    - setup:
        gather_subset:
          - network
          - hardware

# Free strategy (don't wait for all hosts per task)
- hosts: webservers
  strategy: free
  tasks:
    - name: Independent task
      apt:
        name: curl
```

For Mitogen (3-7x speedup), install `mitogen` and set `strategy_plugins` and `strategy = mitogen_linear` in `ansible.cfg`.

## Common Patterns

### Deploy Application

```yaml
- hosts: webservers
  become: yes
  serial: "30%"          # Rolling deploy
  max_fail_percentage: 10

  pre_tasks:
    - name: Remove from load balancer
      uri:
        url: "http://lb.internal/api/remove/{{ inventory_hostname }}"
        method: POST

  roles:
    - app_deploy

  post_tasks:
    - name: Add back to load balancer
      uri:
        url: "http://lb.internal/api/add/{{ inventory_hostname }}"
        method: POST

    - name: Health check
      uri:
        url: "http://localhost:{{ app_port }}/health"
        status_code: 200
      retries: 10
      delay: 3
```

### Setup Users and SSH

```yaml
- name: Configure users
  hosts: all
  become: yes
  tasks:
    - name: Create users
      user:
        name: "{{ item.name }}"
        groups: "{{ item.groups | default([]) }}"
        shell: /bin/bash
      loop: "{{ admin_users }}"

    - name: Add SSH keys
      authorized_key:
        user: "{{ item.name }}"
        key: "{{ item.ssh_key }}"
      loop: "{{ admin_users }}"

    - name: Sudoers entry
      lineinfile:
        path: /etc/sudoers.d/{{ item.name }}
        line: "{{ item.name }} ALL=(ALL) NOPASSWD:ALL"
        create: yes
        mode: "0440"
        validate: "visudo -cf %s"
      loop: "{{ admin_users }}"
      when: item.sudo | default(false)
```
