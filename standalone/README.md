# Standalone RegScale Manager

A Python command-line tool for managing standalone instances of RegScale using
Docker containers.

## Overview

The `standalone_regscale.py` script provides a simple interface to setup
and run a self-contained instance of the RegScale application.

It will automatically download and configure the needed setup files and Docker
images, and provides a thin wrapper around the Docker commands for starting,
stopping, and generally managing the instance.

The script configures and runs two Docker containers - one for the database
(Microsoft SQL Server) and one for the RegScale application - with automatic
environment configuration and credential generation.

## Requirements

### System Requirements
- **Python**: Version 3.10 or higher
- **Docker**: Version 20.10 or higher
- **Operating System**: Windows, Mac OS, or Linux
- **Architecture**: AMD64 only

ARM64 chipsets are not currently supported due to MS SQL Server limitations.

**Note**: Even with Rosetta 2 emulation on ARM-based Mac, MS SQL Server will
not work properly.

### Docker Requirements
- Docker service must be running
- Docker compose must be available
- Sufficient disk space for container images and volumes

If you can run `docker ps` successfully, `standalone_regscale.py` should run
with no issues. On some systems, this may require the user to be in the
`docker` group, if not done automatically when installing Docker.

## Usage

The script takes a command and optional install directory, using the current
directory as a default. To start an new instance, run:

    python standalone_regscale.py start

If you are running on Windows, you may have more luck using the `py` launcher:

    py standalone_regscale.py start

The script can be used to manage multiple instances, each in their own
directory, though only one may be running at a time.

The full set of commands are:

* `setup` - Download and setup local configuration files, called automatically
    by `start` if needed
* `start` - Start the local instance and open a web browser once it is ready
* `stop` - Stop the local instance
* `status` - Stop the local instance
* `update` - Download the latest version of the Docker images, if needed
* `remove` - Deletes the local configuration files, but keeps the images
* `remove-all` - Deletes the lcoal configuration, data, and the images

Aside from `start` opening a web browser and running `setup` if needed, it
as well as the `stop` and `status` commands are mostly wrappers around
`docker compose` commands. The exact commands are shown in the logs.

Use `start` to setup a new instance, as well as run an existing one.
Use `stop` to turn of an instance, `status` to see if it is running,
and `update` to upgrade when a new version is released. Use `remove` to
get rid of an instance's configuration files and data, but you expect to
run another instanace in the future, or `remove-all` if you no longer need
the application at all.

The `--help` option also provides for an overview of usages:

```bash
python standalone_regscale.py --help
```

### Command Options

- `install_dir`: Directory where the standalone instance will be managed
    (defaults to current directory)
- `-v, --verbose`: Increase verbosity (use `-vv` for even more detail)
- `-q, --quiet`: Decrease verbosity (use `-qq` for even less detail)
- `--version`: Display version information
- `--help`: Show help message

## Configuration Files

The script creates three configuration files:

- `atlas.env`: RegScale application environment variables
- `db.env`: Database environment variables
- `docker-compose.yml`: Docker Compose configuration

These files are automatically downloaded from the RegScale community
repository and configured with secure credentials.

Once present, you may customize them as needed.

## Docker Volumes

The script creates two Docker volumes:
- `{install_dir}_atlasvolume`: RegScale application data
- `{install_dir}_sqlvolume`: Database data

These volumes persist data between container restarts.

