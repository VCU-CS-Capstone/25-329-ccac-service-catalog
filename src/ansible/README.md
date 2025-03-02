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

## Running an Ansible playbook on a AWS EC2 Ubuntu 22.04 VM

We have a base Golden Image setup that has already had the [setup-linux](playbook/setup-linux.yml)
and [linux-hardening](playbook/linux-hardening.yml) playbook run on it. This mean this image has
ssh enabled and the `scadmin` user added. Further golden images should be created off of this base
image. Once you have an ansible playbook created that you would like to run to create another 
golden image, follow these instructions. 

### 1. Launch a new VM instance from the Base AMI
1. Once you are in the AWS Console navigate to `EC2` and under `Images`, click on `AMIs`. 
2. Select the `Base-Hardened-Linux` AMI and on the top right click on `launch instance from AMI`
3. On the `Launch an instance` page, make sure the following settings are set for the instance 
    - Create a `Name` for the instance
    - For `Instance type` select `t2.micro`
    - For `Key pair (login)` select `service-catalog`
    - For `Network Settings` click on `Edit` on the top right. 
        - Change `VPC` to `service-catalog-vpc`,
        - For `Subnet` select `service-catalog-subnet-public-1-us-east-1a`
        - For `Auto-assign public IP` select `Enable`
        - For `Firewall (security groups)` click `Select existing security group` and select 
        `Base-SecurityGroup` and any other security group necessary,
    - For `Configure Storage` leave the default(8GiB and gp2)
4. Once settings are configured, click on `Launch instance`
5. Verify the instance has been created and is running by going to `EC2` and clicking on `instances`
under Instances

### 2. Add new EC2 instance to Ansible Inventory
Now that the instance is running, we can add the the VM to the Ansible Inventory so that we can
execute Ansible playbooks on it

1. Select the instance that you have just created in `EC2`
2. In the `Details` section of the instance, find the `Public IPv4 DNS` address and copy it 
3. Add the instance to the [ansible inventory](inventory/inventory.ini) like below, replacing the
`ansible_host` with your instance DNS address
```ini
[ec2_instances]
your-instance-name ansible_host=public-ipv4-dns.amazonaws.com ansible_user=scadmin
```

### 3. Run Ansible Playbook on VM
Now that the EC2 instance has been added to the ansible-playbook, we can now run the ansible
playbook that has been created on that machine. 

**NOTE** If you are running the playbook from a macOS machine, you may need to install sshpass
on your machine. Use `brew install sshpass`

1. SSH into the machine to remove the host-key-checking for your machine to connect to the instance.
You will be required to input the password for the scadmin account as well to finish this step
```sh
ssh scadmin@public-ipv4-dns.amazonaws.com
```
2. After you have successfully SSH into the machine, you can `exit` and return to your local machine.

3. Run your playbook from the src/ansible directory and use the command below. If you playbook
requires additional flags, you can add them here as well. You will then be prompted to input the
password and the BECOME password, which you will input the `scadmin` user password for. 

```sh
ansible-playbook playbook/your-playbook.yml -i inventory/inventory.ini  --ask-pass --ask-become-pass --limit your-instance-name
```
`
