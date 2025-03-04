# Ansible

## What is Ansible?

Ansible is an open-source automation tool that simplifies IT tasks such as configuration management,
application deployment, and infrastructure provisioning. 

## Why Ansible
Agent-less architecture
- Low maintenance overhead by avoiding the installation of additional software across IT 
infrastructure.

Simplicity
- Automation playbooks use straightforward YAML syntax for code that reads like documentation. 
- Ansible is also decentralized, using SSH with existing OS credentials to access to remote machines.

Idempotence and predictability
- When the system is in the state your playbook describes Ansible does not change anything, even if 
the playbook runs multiple times.

##  Ansible Inventories
Inventories organize managed nodes in centralized files that provide Ansible with system information
and network locations. Using an inventory file, Ansible can manage a large number of hosts with a 
single command. Example of an inventory file is shown below:
```ini
[linux]
linux_instance_1 ansible_host=public1-ipv4-dns.amazonaws.com ansible_user=ubuntu
linux_instance_2 ansible_host=public2-ipv4-dns.amazonaws.com ansible_user=ubuntu

[windows]
win_instance_1 ansible_host=public3-ipv4-dns.amazonaws.com ansible_user=admin
win_instance_2 ansible_host=public4-ipv4-dns.amazonaws.com ansible_user=admin
```

## Ansible Playbooks
Playbooks are automation blueprints, in `YAML` format, that Ansible uses to deploy and configure 
managed nodes. Example of a playbook is shown below:
```yaml
- name: My first play
  hosts: myhosts
  tasks:
   - name: Ping my hosts
     ansible.builtin.ping:

   - name: Print message
     ansible.builtin.debug:
       msg: Hello world
```

## Running an Ansible Playbook on a newly created EC2 Instance
Follow these steps in order to run an Ansible Playbook on a newly configured EC2 Instance

### 1. Create a new Ubuntu 22.04 Linux instance
1. In the AWS Console, search for `EC2` and under `Instances` click on `Instances`
2. Click on `Launch Instance` in the top right and enter in the information as below
    - Enter a `Name` for the instance
    - For `Application and OS Images` select `Ubuntu`
    - For `Amazon Machine Image (AMI)` select `Ubuntu Server 22.04 LTS(HVM), SSD Volume Type`
    - For `Instance Type` choose `t2.micro`
    - For `Key pair (login)` select `service-catalog`
    - For `Network Settings` click on `Edit` on the top right. 
        - Change `VPC` to `service-catalog-vpc`,
        - For `Subnet` select `service-catalog-subnet-public-1-us-east-1a`
        - For `Auto-assign public IP` select `Enable`
        - For `Firewall (security groups)` click `Select existing security group` and select 
        `Base-SecurityGroup` and any other security group necessary,
    - For `Configure Storage` leave the default(8GiB and gp2)
3. Once settings are configured, click on `Launch instance`
4. Verify the instance has been created and is running by going to `EC2` and clicking on `instances`
under Instances

### 2. Add the newly created instance to the Ansible inventory
Now that the instance is running, we can add the the VM to the Ansible Inventory so that we can
execute Ansible playbooks on it

1. Select the instance that you have just created in `EC2`
2. In the `Details` section of the instance, find the `Public IPv4 DNS` address and copy it 
3. Add the instance to the [ansible inventory](inventory/inventory.ini) like below, replacing the
`ansible_host` with your instance DNS address
```ini
[ec2_instances]
your-instance-name ansible_host=public-ipv4-dns.amazonaws.com ansible_user=ubuntu
```

### 3. Run the setup-linux Ansible Playbook on VM
Now that the EC2 instance has been added to the ansible inventory, we can now run the [setup-linux](playbook/setup-linux.yml) ansible playbook on that instance. 

1. Run the following command below from the `src/ansible` directory
```sh
ansible-playbook -i inventory/inventory.ini playbook/setup-linux.yml --private-key="path/to/service-catalog.pem" -e "username=demouser password=password"
```

### 4. SSH into instance with newly created user
After the playbook has been run, the SSH settings should be updated to allowed password authenticated
logins without needing the .pem key file and a new user should be created that we can test the login
with.

1. SSH into the machine using the new user and provide password when prompted 
```sh
ssh demouser@public-ipv4-dns.amazonaws.com
```
