#!/bin/bash
# Script used by AWS Lambda to create a new user for each intance that gets created

USERNAME="{user_name}"
PASSWORD=$(openssl passwd -6 "{user_password}") # Uses SHA-512 to hash the inputted password

useradd -m -s /bin/bash "$USERNAME" # Creates new user with home directory and /bin/bash as default shell 
echo "$USERNAME:$PASSWORD" | sudo chpasswd -e # Sets the previously encrypted password to the new user 
usermod -aG sudo "$USERNAME" # Gives the user sudo permissions

