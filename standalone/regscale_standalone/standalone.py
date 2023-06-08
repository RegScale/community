#import standard library modules
import os
import sys
import platform
import webbrowser
import subprocess
import os.path
import string
from pathlib import Path
import secrets
import requests
import importlib.resources
import shutil


def deploy_RegScale():

    check_docker() # ensure docker is installed before proceeding.

    # Confirm where package was installed to know where to access supporting files
    pkg_path = str(importlib.resources.files('regscale_standalone'))
    cwd = str(os.getcwd())
    print(f'Installing setup files into: {cwd}')

    #copy from package installation location to wherever the user wants to run the container from
    ATLAS_FILE = '/atlas.env'
    shutil.copy(pkg_path + ATLAS_FILE, cwd + ATLAS_FILE)
    ATLAS_FILE = cwd + ATLAS_FILE

    DB_FILE = '/db.env'
    shutil.copy(pkg_path + DB_FILE, cwd + DB_FILE)
    DB_FILE = cwd + DB_FILE

    DOCKER_COMPOSE_FILE = '/docker-compose.yml'
    shutil.copy(pkg_path + DOCKER_COMPOSE_FILE, cwd + DOCKER_COMPOSE_FILE)
    DOCKER_COMPOSE_FILE = cwd + DOCKER_COMPOSE_FILE

    REGSCALE_LOCAL = "http://localhost:81"

    user_platform = get_platform()

    print(f'Now deploying RegScale on {user_platform}.')
#=======================================================================================================================
    # Step 1: Pull Docker Container
    print("\nPulling Latest Regscale Docker Container")
    try:
        if user_platform == "Windows":
            os.system("docker pull regscale/regscale:latest")
        else:
            os.system("sudo docker pull regscale/regscale:latest")
        print("Pulling Docker Container Complete")
    except:
        print("Error pulling Docker Container. Unable to complete installation. Exiting installation.")
        sys.exit(1)
# ======================================================================================================================
    # STEP 2: Auto-Create a valid SQL Server PW and write to db.env
    print("Creating SQL Server PW and writing to db.env and atlas.env")
    key_alphabet = string.ascii_letters + string.digits + '!%'
    while True:
        SQL_Server_PW = ''.join(secrets.choice(key_alphabet) for i in range(10))
        if (sum(c.islower() for c in SQL_Server_PW) >= 1
                and sum(c.isupper() for c in SQL_Server_PW) >= 1
                and sum(c.isdigit() for c in SQL_Server_PW) >= 1):
            break
    print("SQL_Server_PW = ", SQL_Server_PW)
    try:
        path = Path(DB_FILE)
        text = path.read_text()
        text = text.replace("YourDBPassword1234WithoutSpecialChars", SQL_Server_PW)
        path.write_text(text)
        print("SQL_Server_PW successfully written to db.env")
    except:
        print("Error writing SQL Server PW to db.env.\nUnable to proceed with installation.")
        sys.exit(1)
# =====================================================================================================================
    # STEP 3: Save PW to atlas.env
    try:
        path = Path(ATLAS_FILE)
        text = path.read_text()
        text = text.replace("YourDBPassword1234WithoutSpecialChars", SQL_Server_PW)
        path.write_text(text)
        print("SQL_Server_PW successfully written to atlas.env")
    except:
        print("Error writing SQL Server PW to atlas.env.\nUnable to proceed with installation.")
        sys.exit(1)
# ======================================================================================================================
    # STEP 4: Auto-Generate a valid JWT Secret Key and save to atlas.env
    print("\nCreating JWT Secret Key, Encryption Key and writing keys to atlas.env")
    while True:
        JWT_Secret_Key = ''.join(secrets.choice(key_alphabet) for i in range(32))
        if (sum(c.islower() for c in JWT_Secret_Key) >= 1
                and sum(c.isupper() for c in JWT_Secret_Key) >= 1
                and sum(c.isdigit() for c in JWT_Secret_Key) >= 1):
            break
    print("JWT_Secret_Key = ", JWT_Secret_Key)
    try:
        path = Path(ATLAS_FILE)
        text = path.read_text()
        text = text.replace("JWTSecretKeyFromSomeWhere6789012", JWT_Secret_Key)
        path.write_text(text)
        print("JWT Secret Key successfully written to atlas.env\n")
    except:
        print("\nError writing JWT Secret Key to atlas.env.\nUnable to proceed with installation.")
        sys.exit(1)
# ======================================================================================================================
    # STEP 5: Auto-Generate a valid Encryption Key Secret Key and save to atlas.env
    while True:
        Encryption_Key = ''.join(secrets.choice(key_alphabet) for i in range(32))
        if (sum(c.islower() for c in Encryption_Key) >= 1
                and sum(c.isupper() for c in Encryption_Key) >= 1
                and sum(c.isdigit() for c in Encryption_Key) >= 1):
            break
    print("Encryption_Key =", Encryption_Key)

    try:
        path = Path(ATLAS_FILE)
        text = path.read_text()
        text = text.replace("YourEncryptionKeyFromSomeWhere12", Encryption_Key)
        path.write_text(text)
        print("Encryption Key successfully written to atlas.env\n")
    except:
        print("\nError writing Encryption Key to atlas.env.\nUnable to proceed with installation.")
        sys.exit(1)
# =======================================================================================================================
    # STEP 6: Convert files for ARM64 platform (Macs with M1, M2 chips)
    if platform.machine() == 'arm64':
        print("Updating files for Mac ARM64 platform\n")
        update_docker_compose_arm64(DOCKER_COMPOSE_FILE)
        update_db_env_arm64(DB_FILE)
# =======================================================================================================================
    # STEP 7: Start Docker-Compose to bring RegScale container and SQL server container up
    print("Running RegScale using Docker-compose\n")
    docker_command = 'docker-compose'
    #Determine if using docker compose v1 or v2
    try:
        subprocess.check_output('docker compose version', shell=True)
        print('Confirmed docker compose v2 command is available.')
        docker_command = 'docker compose'
    except:
        print('Current docker compose version is not v2. Proceeding with v1.')
    try:
        if user_platform == "Windows":
            os.system(docker_command + " up -d")
        else:
            # Run behind the scenes -- Linux and Mac need sudo
            os.system("sudo " + docker_command + " up -d")
        # Open Local version of RegScale
        webbrowser.open(REGSCALE_LOCAL, new=2)
    except:
        print("Docker Compose Error. Unable to complete installation.\n")
        sys.exit(1)
    return
#==============================DOCKER_COMPOSE_FILE=========================================================================================
def check_docker():
    print('\nChecking status of Docker installation...')
    try:
        # Is Docker Installed?
        subprocess.check_output('docker --version', shell=True)
        print("Confirmed Docker is installed.\n")
        # Docker is Installed, but is it Running?
    except:
        print("Docker is required, but unable to detect Docker installation. Exiting script.")
        sys.exit(1)
    try:
        subprocess.check_output('docker ps', shell=True)
        print("Confirmed Docker Is Running.")
    except:
        print("Docker is installed, but not running. Please start Docker and run this script again.")
        sys.exit(1)

def get_platform():
    try:
        if platform.system() in ["Windows", "Linux"]:
            return(platform.system())
        elif platform.system() == "Darwin":
            return("Mac")
    except:
        print("Operating system unknown\n RegScale can be installed on Windows, Mac, or Linux. Exiting installation.")
        sys.exit(1)

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

def update_db_env_arm64(db_env_file):
    """Update db.env to use Azure SQL Edge instead of MS SQL"""
    try:
        path = Path(db_env_file)
        text = path.read_text()
        text = text.replace("ACCEPT_EULA=Y", "ACCEPT_EULA=1")
        text = text.replace("MSSQL_PID=Express", "MSSQL_PID=Developer")
        path.write_text(text)
        print("Updated db.env to use Azure SQL Edge\n")
    except:
        print("Updating db.env to use Azure SQL Edge Error\n")
    return


