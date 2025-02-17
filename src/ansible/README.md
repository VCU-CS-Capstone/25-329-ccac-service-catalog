# Ansible Setup Guide

## What is Ansible?

Ansible is an open-source automation tool that simplifies IT tasks such as configuration management, application deployment, and infrastructure provisioning. It allows you to automate the management of virtual servers using simple YAML-based scripts called playbooks.

## Use Case: Provisioning Virtual Servers

Ansible is widely used for provisioning and configuring virtual servers. It allows you to:
- Automate server setup and configuration.
- Ensure consistency across multiple servers.
- Reduce manual errors and deployment time.

## Setting Up a Virtual Machine for Ansible

Follow these steps to configure a Virtual Machine (VM) to allow Ansible to run on it from your local machine.

### 1. Generate SSH Key on Mac/Linux
If you haven't already, generate an SSH key pair on your local machine:

```sh
ssh-keygen -t rsa -b 4096
```

### 2. Copy SSH Key to Ubuntu VM
Copy your public SSH key from your local machine to the Ubuntu VM:

```sh
ssh-copy-id -p 2222 username@vm-ip-address
```

Replace `username` with your Ubuntu VM username.

### 3. Configure Ansible Inventory
Create an Ansible inventory file on your Mac, e.g., `inventory.ini`:

```ini
[linux]
ubuntu ansible_host=vm-ip-address ansible_port=22 ansible_user=your_username
```

Replace `vm-ip-address` with your Ubuntu VM IP Address, `ansible_port` with the necessary port, and
`your_username` with your Ubuntu VM username.

### 4. Create Ansible Configuration File
Create an `ansible.cfg` file in the same directory as your playbook:

```ini
[defaults]
inventory = ./inventory.ini
host_key_checking = False
```
Replace `./inventory.ini` with the location of your inventory file


### 5. Verify Ansible Setup with a Test Playbook
Create a simple Ansible playbook named test_playbook.yml to verify that Ansible can run correctly on
the VM:
```yaml
- name: Test Ansible Connection
  hosts: *linux*
  become: yes
  tasks:
    - name: Ping the server
      ping:
    - name: Check current user
      command: whoami
```
Run the playbook using the following command:
```sh
ansible-playbook path/to/test_playbook.yml --inventory path/to/inventory.ini --ask-become-pass
```
The `--ask-become-pass` flag prompts for the sudo password, which is required for privilege escalation.

Your VM is now ready to be managed using Ansible!

