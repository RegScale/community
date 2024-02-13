![RegScale automates GRC compliance](https://regscale.com/wp-content/uploads/2023/01/RegScale_logo_main.svg)

# RegScale Stand-alone Installer

[RegScale](https://regscale.com/) shifts compliance left by bridging the divide between cybersecurity and compliance. This repository is for sharing scripts, integrations, and other automations with the RegScale community.

### Requirements

 * Python 3.9 or higher.
 * Docker Engine is installed. 
 * Any applicable post-installation steps for docker configuration are complete. (For example, on Linux the user must be [added to docker group](https://docs.docker.com/engine/install/linux-postinstall/).)
 * pip is installed. You can confirm with `pip list` or `pip3 list`. If not installed: Linux `sudo apt-get install python3-pip` or `yum install python3-pip`. For Windows see official [documentation](https://pip.pypa.io/en/stable/installation/).
 * Following best practice, we will install using a virtual environment. You can use the virtual environment of your choice, but these instructions will assume [virtualenv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#installing-virtualenv) is installed. For example, on Debian systems using apt: `sudo apt install python3-virtualenv` or `py -m pip install --user virtualenv` on Windows.

### Instructions for Installation
* Make a directory for installation.
* Download `regscale_standalone.zip` into the installation directory.
* Create a virtual environment (`virtualenv reg_env`) and then activate it (`source reg_env/bin/activate`)
* Install RegScale Standalone:   `pip install regscale_standalone.zip` or `pip3 install regscale_standalone.zip`
* Run the installation with the following command:  `regscale-standalone install`

### Instructions for Tear Down

* Navigate to the directory in which you installed RegScale's configuration files.
* Run the teardown process with `regscale-standalone teardown` to stop the application, purge configuration files, and remove related docker resources.