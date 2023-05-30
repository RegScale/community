# If a password error occurs, you need to prune the atlas volumes that may be stranded "docker volume prune "

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
import importlib

# install 3rd party libraries if not already present in environment.
PACKAGE_LIST = ['requests', 'docker']
for library in PACKAGE_LIST:
    try:
        globals()[library] = importlib.import_module(library)
    except ModuleNotFoundError:
        print(f'Installing missing python dependency: {library}')
        try:
            os.system(f'pip3 install {library}')
            globals()[library] = importlib.import_module(library)
        except Exception as e:
            print(f'Unknown error installing dependency: {e}.\n\nExiting program.')
            sys.exit(1)
    except Exception as e:
        print(f'Unknown error referencing dependency: {e}.\n\nExiting program.')
        sys.exit(1)


#=======================================================================================================================
ATLAS_FILE = 'atlas.env'
DB_FILE = 'db.env'
DOCKER_COMPOSE_FILE = 'docker-compose.yml'

CONFIG_FILE_URLS = {
    ATLAS_FILE: 'https://raw.githubusercontent.com/RegScale/community/main/standalone/atlas.env',
    DB_FILE: 'https://raw.githubusercontent.com/RegScale/community/main/standalone/db.env',
    DOCKER_COMPOSE_FILE: 'https://raw.githubusercontent.com/RegScale/community/main/standalone/docker-compose.yml'}

REGSCALE_LOCAL = "http://localhost:81"
#=======================================================================================================================
def main():

    user_platform = get_platform()
    check_docker(user_platform)
    deploy_RegScale(user_platform)

#=======================================================================================================================

def get_platform():
    try:
        if platform.system() in ["Windows","Linux"]:
            return(platform.system())
        elif platform.system() == "Darwin":
            return("Mac")
    except:
        print("Operating system unknown.\n RegScale can be installed on Windows, Mac, or Linux. Exiting installation.")
        sys.exit(1)

def check_docker(platform):
    print('\nChecking status of Docker installation...')
    dockerIsRunning = False
    try:
        # Is Docker Installed?
        subprocess.check_output('docker --version', shell=True)
        print("Confirmed Docker is installed.\n")
        # Docker is Installed, but is it Running?
        try:
            subprocess.check_output('docker ps', shell=True)
            print("Docker Is Running")
        except:
            print("Docker is installed, but not running. Please start Docker and run this script again.")
            sys.exit(1)
    except:
        print("Docker is required, but unable to detect Docker installation. Exiting script.")
        sys.exit(1)

def deploy_RegScale(user_platform):

    print(f'Now deploying RegScale on {user_platform}.')

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

    # STEP 2: Download and Install Config Files
    print("\nDownloading Config Files")
    for i, (file_name, file_url) in enumerate(CONFIG_FILE_URLS.items()):
        try:
            # Check if local file exists
            if os.path.exists(file_name):
                print(f'File {file_name} already exists')
            else:
                print(f'Creating file {file_name}.')
                data = requests.get(file_url)
                with open(file_name, "wb") as file:
                    file.write(data.content)
        except Exception as e:
            print(e)
            print(f'\nError downloading {file_name}. Unable to complete installation.\n')
            sys.exit(1)

    # STEP 3: Auto-Create a valid SQL Server PW and write to db.env
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

    # STEP 4: Save PW to atlas.env
    try:
        path = Path(ATLAS_FILE)
        text = path.read_text()
        text = text.replace("YourDBPassword1234WithoutSpecialChars", SQL_Server_PW)
        path.write_text(text)
        print("SQL_Server_PW successfully written to atlas.env")
    except:
        print("Error writing SQL Server PW to atlas.env.\nUnable to proceed with installation.")
        sys.exit(1)

    # STEP 5: Auto-Generate a valid JWT Secret Key and save to atlas.env
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

    # STEP 6: Auto-Generate a valid Encryption Key Secret Key and save to atlas.env
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

    # STEP 7: Convert files for ARM64 platform (Macs with M1, M2 chips)
    if platform.machine() == 'arm64':
        print("Updating files for Mac ARM64 platform\n")
        update_docker_compose_arm64(DOCKER_COMPOSE_FILE)
        update_db_env_arm64(DB_FILE)

    # STEP 8: Start Docker-Compose to bring RegScale container and SQL server container up
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
        if platform.system() in "Windows":
            os.system(docker_command + " up -d")
        else:
            # Run behind the scenes -- Linux and Mac need sudo
            os.system("sudo " + docker_command + " up -d")
        # Open Local version of RegScale
        webbrowser.open(REGSCALE_LOCAL, new=2)
    except:
        print("Docker Compose Error\n")
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

if __name__ == '__main__':
    main()