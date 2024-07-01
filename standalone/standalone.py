from multiprocessing.connection import wait
import os
import sys
import platform
import webbrowser
import subprocess
import os.path
import string
import time
#from tkinter import *
from pathlib import Path

# If a password error occurs, you need to prune the atlas volumes that may be stranded "docker volume prune "
# Use Pip3 and Python3 if Python3 and Python2 are both installed. Some of the libraries won't download on Python2

#There may be modules that don't exist so need to set up try/except and install them with pip3

# Import secrets if it doesn't exist
try:
    import secrets
except ModuleNotFoundError:
    os.system("pip3 install secrets")
    import secrets


# Import requests if it doesn't exist
try:
    import requests
except ModuleNotFoundError:
    os.system("pip3 install requests")
    import requests

# Import Docker if it doesn't exist
try:
    import docker
except ModuleNotFoundError:
    os.system("pip3 install docker")
    import docker

def config_and_deploy():
    # Install RegScale
    # Step 1: Pull Docker Container 
    print("\nPulling Latest Regscale Docker Container")
    try:
        if platform.system() in "Windows":
            os.system("docker pull regscale/regscale:latest")
        else:
            os.system("sudo docker pull regscale/regscale:latest")
        print("Pulling Docker Container Complete") 
    except:
        print("Error pulling Docker Container. Please install Docker rerun this script. Exiting script")
        sys.exit()

    # URLs for config files
    atlas_env = "https://raw.githubusercontent.com/RegScale/community/main/standalone/atlas.env"
    atlas_local_file = "atlas.env"
    db_env = "https://raw.githubusercontent.com/RegScale/community/main/standalone/db.env"
    db_local_file = "db.env"
    docker_compose_yml = "https://raw.githubusercontent.com/RegScale/community/main/standalone/docker-compose.yml"
    docker_compose_local_file = "docker-compose.yml"
    regScale_Local = "http://localhost:81"

    # Step 2: Download and Install Config Files
    # To Do: Create a function to download the files instead of putting all in here
    print("\nDownloading Config Files")
    try:
        # Check if atlas.env local file exists
        if os.path.exists(atlas_local_file):
            print("atlas.env file already exists")
        else:
            print("Create atlas.env file")
            data = requests.get(atlas_env)
            with open(atlas_local_file, "wb") as file:
                file.write(data.content)
    except:
        print("Error downloading atlas.env file\n") 

    # Check if db.env file exists
    try:
        if os.path.exists(db_local_file):
            print("db.env file already exists")
        else:
            print("Create db.env file")
            data = requests.get(db_env)
            with open(db_local_file, "wb") as file:
                file.write(data.content)
    except:
        print("Error downloading db.env file\n") 

    # Check if docker-compose.yml file exists
    try:
        if os.path.exists(docker_compose_local_file):
            print("docker-compose.yml file already exists")
        else:
            print("Create docker-compose.yml file")
            data = requests.get(docker_compose_yml)
            with open(docker_compose_local_file, "wb") as file:
                file.write(data.content)
    except:
        print("Error downloading docker-compose.yml file\n") 

    # Step 3: Auto-Create a valid SQL Server PW and write to db.env
    print("Creating SQL Server PW and writing to db.env and atlas.env")
    key_alphabet = string.ascii_letters + string.digits + '!%'
    while True:
        SQL_Server_PW = ''.join(secrets.choice(key_alphabet) for i in range(10))
        if (sum(c.islower() for c in SQL_Server_PW) >=1
                and sum(c.isupper() for c in SQL_Server_PW) >=1
                and sum(c.isdigit() for c in SQL_Server_PW) >=1):
            break
    print("SQL_Server_PW = ", SQL_Server_PW)
    
    try:
        path = Path(db_local_file)
        text = path.read_text()
        text = text.replace("YourDBPassword1234WithoutSpecialChars", SQL_Server_PW)
        path.write_text(text)
        print("SQL_Server_PW successfully written to db.env")
    except:
        print("Error writing SQL Server PW to db.env")        

    # Step 4: Save PW to atlas.env
    try:
        path = Path(atlas_local_file)
        text = path.read_text()
        text = text.replace("YourDBPassword1234WithoutSpecialChars", SQL_Server_PW)
        path.write_text(text)
        print("SQL_Server_PW successfully written to atlas.env")
    except:
        print("Error writing SQL Server PW to atlas.env")        

    # Step 5: Auto-Generate a valid JWT Secret Key and save to atlas.env
    print("\nCreating JWT Secret Key, Encryption Key and writing keys to atlas.env")
    while True:
        JWT_Secret_Key = ''.join(secrets.choice(key_alphabet) for i in range(32))
        if (sum(c.islower() for c in JWT_Secret_Key) >=1
                and sum(c.isupper() for c in JWT_Secret_Key) >=1
                and sum(c.isdigit() for c in JWT_Secret_Key) >=1):
            break
    print("JWT_Secret_Key = ", JWT_Secret_Key)
    
    try:
        path = Path(atlas_local_file)
        text = path.read_text()
        text = text.replace("JWTSecretKeyFromSomeWhere6789012", JWT_Secret_Key)
        path.write_text(text)
        print("JWT Secret Key successfully written to atlas.env\n")
    except:
        print("\nError writing JWT Secret Key to atlas.env")        

    # Step 6: Auto-Generate a valid Encryption Key Secret Key and save to atlas.env
    while True:
        Encryption_Key = ''.join(secrets.choice(key_alphabet) for i in range(32))
        if (sum(c.islower() for c in Encryption_Key) >=1
                and sum(c.isupper() for c in Encryption_Key) >=1
                and sum(c.isdigit() for c in Encryption_Key) >=1):
            break
    print("Encryption_Key =", Encryption_Key)

    try:
        path = Path(atlas_local_file)
        text = path.read_text()
        text = text.replace("YourEncryptionKeyFromSomeWhere12", Encryption_Key)
        path.write_text(text)
        print("Encryption Key successfully written to atlas.env\n")
    except:
        print("\nError writing Encryption Key to atlas.env\n")

    # Step 7: Convert files for ARM64 platform (Macs with M1, M2 chips)
    if platform.machine() == 'arm64':
        print("Updating files for Mac ARM64 platform\n")
        update_docker_compose_arm64(docker_compose_local_file)
        update_db_env_arm64(db_local_file)

    # Step 8: Start Docker-Compose to bring RegScale container and SQL server container up
    print("Running RegScale using Docker-compose\n")
    try:
        if platform.system() in "Windows":
            os.system("docker-compose up -d")
        else:
            # Run behind the scenes -- Linux and Mac need sudo
            os.system("sudo docker-compose up -d")
        #print("\nWaiting for RegScale to start a browser will open soon")        
        #time.sleep(5)
        #Open Local version of RegScale
        webbrowser.open(regScale_Local, new=2)
    except:
        print("Docker Compose Error\n")
    return

def deploy_RegScale_Windows():
    dockerDesktopWindows = "https://docs.docker.com/desktop/windows/install/"
    dockerDesktopMac = "https://docs.docker.com/desktop/mac/install/"
    dockerDesktopLinux = "https://docs.docker.com/desktop/linux/install/"
    dockerIsInstalled = False
    dockerIsRunning = False

    # Check for Docker Installation
    print("Deploying RegScale in Windows")
    
    try:
        # Is Docker Installed?
        subprocess.check_output('docker --version', shell=True)
        dockerIsInstalled = True
        print ("Docker Is Installed = ", dockerIsInstalled)
        # Docker is Installed, but is it Running?
        try:
            subprocess.check_output('docker ps', shell=True)
            dockerIsRunning = True
            print ("Docker Is Running = ", dockerIsRunning)
        except:
            dockerIsRunning = False
            print("Docker is installed, but not running. Start Docker Desktop and rerun this script. Exiting script")
            sys.exit()
    except:
        dockerIsRunning = False
        dockerIsInstalled = False
        print("Docker Error. Please install Docker Desktop for Windows and rerun this script. Exiting script")
        sys.exit()
    
    if dockerIsInstalled:
        config_and_deploy()
    return

def deploy_RegScale_Mac():
    # Check for Docker Installation
    print("Deploying RegScale in Mac")
    try:
        # Is Docker Installed?
        subprocess.check_output('sudo docker version', shell=True)
        dockerIsInstalled = True
        print ("Docker Is Installed = ", dockerIsInstalled)
    
        # Docker is Installed, but is it Running?
        try:
            subprocess.check_output('docker ps', shell=True)
            dockerIsRunning = True
            print ("Docker Is Running = ", dockerIsRunning)
        except:
            dockerIsRunning = False
            print("Docker is installed, but not running. Start Docker Desktop and rerun this script")
            print("Exiting script")
            
    except:
        dockerIsRunning = False
        dockerIsInstalled = False
        print("Docker is not installed. Please install Docker Desktop for Mac and rerun this script")
        print("Exiting script")
        sys.exit()

    if dockerIsInstalled:
        config_and_deploy()
    return

def deploy_RegScale_Linux():
    # Check for Docker Installation
    print("Deploying RegScale in Linux")
    try:
        # Is Docker Installed?
        subprocess.check_output('docker --version', shell=True)
        dockerIsInstalled = True
        print ("Docker Is Installed = ", dockerIsInstalled)
    
        # Docker is Installed, but is it Running?
        try:
            subprocess.check_output('docker ps', shell=True)
            dockerIsRunning = True
            print ("Docker Is Running = ", dockerIsRunning)
        except:
            dockerIsRunning = False
            print("Docker is installed, but not running. Starting Docker")
            # START DOCKER IN LINUX
            os.system("sudo service docker start")
            #os.system("sudo systemctl docker start")
            
    except:
        dockerIsRunning = False
        dockerIsInstalled = False
        print("Docker Error. Exiting script")
        sys.exit()

    if dockerIsInstalled:
        config_and_deploy()
    return

def update_docker_compose_arm64(env_file):
    """Update docker-compose.yml to use Azure SQL Edge instead of MS SQL"""
    try:
        path = Path(env_file)
        text = path.read_text()
        text = text.replace("mcr.microsoft.com/mssql/server:2019-latest", "mcr.microsoft.com/azure-sql-edge")
        path.write_text(text)
        print("Updated docker-compose to use Azure SQL Edge\n")
    except:
        print("Updating docker-compose to use Azure SQL Edge Error\n")
    return

def update_db_env_arm64(env_file):
    """Update db.env to use Azure SQL Edge instead of MS SQL"""
    try:
        path = Path(env_file)
        text = path.read_text()
        text = text.replace("ACCEPT_EULA=Y", "ACCEPT_EULA=1")
        text = text.replace("MSSQL_PID=Express", "MSSQL_PID=Developer")
        path.write_text(text)
        print("Updated db.env to use Azure SQL Edge\n")
    except:
        print("Updating db.env to use Azure SQL Edge Error\n")
    return

# Check for OS  Windows, Mac, Linux
def check_os():
    platformName = platform.system() 
    if platformName in "Windows":
        #print("platform.system:",platformName)
        print("Deploy RegScale in Windows")
        deploy_RegScale_Windows()
    elif platformName in "Darwin":
        print("Deploy RegScale in Mac")
        deploy_RegScale_Mac()
    elif platformName in "Linux":
        print("Deploy RegScale in Linux")
        deploy_RegScale_Linux()
    else:
        print("Operating system unknown\n RegScale can be installed on Windows, Mac, or Linux\n")
        print("Exiting script")
        sys.exit()
    #print("platform.release:",platform.release())
    return

# Run check_os function and deploy in the current platform    
check_os()
