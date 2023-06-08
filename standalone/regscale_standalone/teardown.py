# run this file from within the installation directory.
import os
import subprocess
import sys

ATLAS_FILE = 'atlas.env'
DB_FILE = 'db.env'
DOCKER_COMPOSE_FILE = 'docker-compose.yml'

def teardown():
    print('\nInitiating tear down! This process deletes configuration files and supporting docker volumes.\n')
    if os.path.exists(ATLAS_FILE) and os.path.exists(DB_FILE) and os.path.exists(DOCKER_COMPOSE_FILE):

        print(f'Preparing to delete application docker volumes and the following files as part of cleanup:\n\n'
              f'\t - {ATLAS_FILE}\n'
              f'\t - {DB_FILE}\n'
              f'\t - {DOCKER_COMPOSE_FILE}\n')

        response = input('Enter Y to continue or any other key to cancel:  ')
        if response.lower() == 'y':
            ################################################################################################################
            docker_command = 'docker-compose'
            # Determine if using docker compose v1 or v2
            try:
                subprocess.check_output('docker compose version', shell=True)
                print('Confirmed docker ycompose v2 command is available.')
                docker_command = 'docker compose'
            except:
                print('Current docker compose version is not v2. Proceeding with v1.')
            try:
                # remove docker volumes
                os.system(docker_command + " down")
                os.system("docker volume rm " + os.path.split(os.getcwd())[1] + "_atlasvolume")
                os.system("docker volume rm " + os.path.split(os.getcwd())[1] + "_sqlvolume")
                print('Removed docker volumes.')
            except:
                print("Problem removing docker volumes.")
                ########################################################################################################
            try:
                os.remove(ATLAS_FILE)
                os.remove(DB_FILE)
                os.remove(DOCKER_COMPOSE_FILE)
                print("Configuration files deleted.")
            except:
                print('Unknown problem removing configuration files.')

            print('Teardown is complete.')

        else:
            print('Teardown process cancelled. No files or resources have been altered.')

    else:
        print('One or more configuration files were not found. Please confirm you are in the installation directory for'
              'RegScale Standalone, then run teardown again.')
        sys.exit()