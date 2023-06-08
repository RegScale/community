![RegScale automates GRC compliance](https://regscale.com/wp-content/uploads/2023/01/RegScale_logo_main.svg)

# RegScale Stand-alone Installer

[RegScale](https://regscale.com/) shifts compliance left by bridging the divide between cybersecurity and compliance. This repository is for sharing scripts, integrations, and other automations with the RegScale community.

### Requirements

 * Python 3.9 or higher.
 * Docker Engine is installed. 
 * Any applicable post-installation steps for docker configuration are complete. (For example, on Linux the user must be added to docker group.)
 * pip is installed.
 * Following best practice, we will install using a virtual environment. You can use the virtual environment of your choice, but these instructions will assume [virtualenv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#installing-virtualenv) is installed. 

### Instructions for Installation
* Make a directory for installation.
* Download regscale_standalone.zip into the installation directory.
* Create a virtual environment (`virtualenv standalone`) and then activate it (`source standalone/bin/activate`)
* Install RegScale Standalone:   `pip install regscale_standalone.zip` or `pip3 install regscale_standalone.zip`
* Run the installation with the following command:  `regscale-standalone install`

### Instructions for Tear Down

* Navigate to the directory in which you installed RegScale's configuration files.
* Run the teardown process with `regscale-standalone teardown` to stop the application, purge configuration files, and remove related docker resources.