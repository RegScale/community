#!/usr/bin/env python
"""standalone_regscale.py - Manage a standalone instance of Regscale

This configures and runs two docker containers, one for the database and one
for the application, each with their own environment file and a docker compose
file to manage them.
"""

import argparse
import logging
import os
import os.path
import platform
import random
import re
import string
import subprocess
import sys
import time
import urllib.request
import webbrowser

__version__ = "2.0.0"
__author__ = "echerry@regscale.com"

LOG = logging.getLogger(__name__)
DEFAULT_LOG_LEVEL = logging.INFO
CONFIG_FILES_URL = (
    "https://raw.githubusercontent.com/RegScale/community/main/standalone"
)
ATLAS_ENV_FILE = "atlas.env"
DB_ENV_FILE = "db.env"
DOCKER_COMPOSE_YAML_FILE = "docker-compose.yml"
CONFIG_FILES = (
    ATLAS_ENV_FILE,
    DB_ENV_FILE,
    DOCKER_COMPOSE_YAML_FILE,
)

_LOG_LEVELS = (
    logging.CRITICAL + 5,
    logging.CRITICAL,
    logging.ERROR,
    logging.WARNING,
    logging.INFO,
    logging.DEBUG,
    logging.DEBUG - 5,
)
_STANDALONE_URL = "http://localhost"
_STARTUP_CHECK_DELAY_SECS = 10
_DOCKER_CMDS = {
    "start": (
        'docker compose -f "{compose_file}" up -d',
        "Starting up a standalone RegScale instance in %r.",
    ),
    "stop": (
        'docker compose -f "{compose_file}" down',
        "Stopping standalone RegScale instance in %r.",
    ),
    "status": (
        'docker compose -f "{compose_file}" ps',
        "Showing active standalone RegScale containers for %r.",
    ),
}
_AMBIGUOUS_CHARS = {"I", "l", "1", "0", "O", "S", "5", "Z", "2", "B", "8"}
_CLEAR_LETTERS = "".join(
    {char for char in string.ascii_letters if char not in _AMBIGUOUS_CHARS}
)
_CLEAR_DIGITS = "".join(
    {char for char in string.digits if char not in _AMBIGUOUS_CHARS}
)
_CLEAR_SPECIALS = "_.-+"
_CLEAR_CHARS = _CLEAR_LETTERS + _CLEAR_DIGITS + _CLEAR_SPECIALS


def generate_secret(length: int) -> str:
    """Generate a randomized, typable secret of the given length.

    Typeable is meant to be both easy to type and with no characters that
    need to be escaped.

    It also ensures there is at least one lowercase, uppercase, digit,
    and symbol to meet MS SQL Server default password requirements.
    """
    # The four here is a fixed value that can never be changed since
    # the password rules require one of four different character types.
    if length < 4:  # noqa
        raise ValueError(
            f"Cannot generate a secret of length {length}! (minimum 4)"
        )
    chars = [
        random.choice(_CLEAR_LETTERS).upper(),
        random.choice(_CLEAR_LETTERS).lower(),
        random.choice(_CLEAR_DIGITS),
        random.choice(_CLEAR_SPECIALS),
    ]
    while len(chars) < length:
        chars.append(random.choice(_CLEAR_CHARS))
    random.shuffle(chars)
    return "".join(chars)


def update_text(
    text: str, prefix: str | None, suffix: str | None, new_value: str
) -> str:
    """Returns a copy of te text with the content between prefix and suffix
    replaced with the new value.

    If prefix or suffix is None, they will instead be matched agaist the
    start or the end of the line, respectively.

    """
    pattern = (
        (re.escape(prefix) if prefix else "^")
        + r"(.*?)"
        + (re.escape(suffix) if suffix else "$")
    )
    replacement = (
        (prefix if prefix else "") + new_value + (suffix if suffix else "")
    )
    return re.sub(pattern, replacement, text)


def run_command(
    command: str, cwd: str = os.curdir, show_output: bool = True
) -> subprocess.CompletedProcess[str]:
    """Run the given command with subprocess.run, and return the result or
    log any error before re-raising it.
    """
    LOG.debug("Running command %r in %r.", command, cwd)
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            stderr=subprocess.PIPE,
            stdout=None if show_output else subprocess.PIPE,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as err:
        LOG.exception(
            "Error (exit code %s) running command %r in %r. Errors: %s",
            err.returncode,
            command,
            cwd,
            err.stderr.strip(),
        )
        raise
    LOG.debug("Command completed: %r", result)
    return result


def ensure_config_file_exists(
    config_file: str,
    install_dir: str = os.curdir,
    config_files_url: str = CONFIG_FILES_URL,
) -> None:
    """Download a copy of the config if no local copy exists."""
    install_dir = os.path.abspath(install_dir)
    file_path = os.path.join(install_dir, config_file)
    if os.path.exists(file_path):
        LOG.info("Using existing config file: %r", file_path)
        return
    try:
        config_url = f"{config_files_url}/{config_file}"
        LOG.info("Downloading default config file: %r", config_url)
        with (
            open(file_path, "w", encoding="utf-8") as output_file,
            urllib.request.urlopen(config_url) as input_file
        ):
                output_file.write(input_file.read().decode("utf-8"))
    except Exception:
        LOG.exception(
            "Could not read default config file %r from %r!",
            file_path,
            config_url,
        )
        raise


def check_requirements(install_dir: str = os.curdir) -> None:
    """Raise an exception unless docker 20.10 or later is found and running.
    Warn if the operating system is not officially supported.

    """

    if platform.system() not in ("Windows", "Darwin", "Linux"):
        LOG.warning(
            "Unknown platform %r! Currently, only Windows, "
            "Darwin (Mac OS X) and Linux are officially supported.",
            platform.system(),
        )

    try:
        LOG.debug("Checking that docker is installed.")
        result = run_command(
            "docker --version", install_dir, show_output=False
        )
        # The output should be of the form:
        # Docker version 27.5.1, build 27.5.1-0ubuntu3~24.04.2
        docker_version = result.stdout.split(" ")[2][:-1]
        docker_major, docker_minor = (
            int(version) for version in docker_version.split(".")[0:2]
        )
        # Require docker 20.10 or higher.
        if docker_major < 20 or (docker_major == 20 and docker_minor < 10):  # noqa
            message = (
                "Docker version 20.10 or higher is required. "
                f"Currently installed verison: {docker_version}"
            )
            LOG.error(message)
            raise OSError(message)
    except subprocess.CalledProcessError:
        LOG.exception(
            "Cannot find the docker command! Make sure it is installed and "
            "runnable by the current user:",
        )
        raise

    try:
        LOG.debug("Checking that the docker service is running.")
        run_command("docker ps", install_dir, show_output=False)
    except subprocess.CalledProcessError:
        LOG.exception("The docker service does not appear to be running:")
        raise


def update_config(
    config_file: str, updates: tuple[tuple[str, str | None, str], ...]
) -> None:
    """Apply the given updates to the config file, where an update is the
    prefix, suffix, and new value arguments to a update_text() call.
    """
    try:
        LOG.debug("Reading config file: %r", config_file)
        with open(config_file, encoding="utf=8") as file_handle:
            text = file_handle.read()
        for update in updates:
            prefix, suffix, new_value = update
            text = update_text(text, prefix, suffix, new_value)
        LOG.debug("Writing updated config file: %r", config_file)
        with open(config_file, "w", encoding="utf-8") as file_handle:
            file_handle.write(text)
    except OSError:
        LOG.exception("Error updating config file %r:", config_file)
        raise


def setup(install_dir: str = os.curdir) -> None:
    "Setup the standalone regscale instance at the given path."

    LOG.info("Setting up standalone RegScale instance in %r.", install_dir)

    LOG.info("Ensuring we have all needed config files.")
    for config_file in CONFIG_FILES:
        ensure_config_file_exists(config_file, install_dir)

    LOG.info("Updating config files.")

    db_env_path = os.path.join(install_dir, DB_ENV_FILE)
    atlas_env_path = os.path.join(install_dir, ATLAS_ENV_FILE)

    # On an M1, M2, M3 or other ARM-baset machine, we can't run MS SQL Server.

    # We check the version name instead of platform.machine() in case we are
    # on a Mac which is using Rosetta stone to emulating the amd64
    # architecture, which won't work.
    if (platform.machine() == "arm64") or (
        "arm64" in platform.version().lower()
    ):
        LOG.warning(
            "The RegScale standalone instance requires MS SQL Server, "
            "which does not support the dected ARM64 architecture, even when "
            "AMD64 is emulated. This is most common on newer Macs. If you "
            "have problems you may be able to manually edit the docker "
            "compose file %r to point at an instance of MS SQL Server running "
            "on supported AMD64 architecture, though it is likely easier to "
            "simply run the standalone RegScale there instead."
        )

    db_key = generate_secret(12)
    update_config(
        db_env_path,
        (("SA_PASSWORD=", None, db_key),),
    )
    update_config(
        atlas_env_path,
        (
            ("Password=", ";", db_key),
            ("JWTSecretKey=", "\n", generate_secret(32)),
            ("EncryptionKey=", "\n", generate_secret(64)),
        ),
    )

    LOG.warning(
        "Updated %r and %r with new credentials. Please ensure they "
        "have the appropriate access restrictions.",
        db_env_path,
        atlas_env_path,
    )

    update_images(install_dir)

    LOG.info("Setup complete.")


def update_images(install_dir: str = os.curdir) -> None:
    """Run docker pull with os.system() so we see real time updatess."""
    docker_compose_path = os.path.join(install_dir, DOCKER_COMPOSE_YAML_FILE)
    LOG.info(
        "Updating standalone RegScale images for %r.", docker_compose_path
    )
    command = f'docker compose -f "{docker_compose_path}" pull'
    # Use os.system() so docker shows lives updates on download status if
    # were in an interactive terminal.
    LOG.debug("Running command: %r", command)
    result = os.system(command)
    if result:
        message = f"Error (exit code {result}) running command: {command!r}"
        LOG.error(message)
        raise OSError(message)


def remove(install_dir: str = os.curdir, remove_images: bool = False) -> None:
    "Remove the standalone regscale instance at the given path."
    install_dir = os.path.abspath(install_dir)
    LOG.info("Removing standalone RegScale instance from %r.", install_dir)
    errors = []

    # Run the various docker cleanup commands.
    commands = (
        (
            "docker compose -f "
            f'"{os.path.join(install_dir, DOCKER_COMPOSE_YAML_FILE)}" down '
            + ("--rmi all" if remove_images else "")
        ),
        f"docker volume rm {os.path.basename(install_dir)}_atlasvolume",
        f"docker volume rm {os.path.basename(install_dir)}_sqlvolume",
    )
    LOG.info(
        "Removing docker%s volumes.", (" images and" if remove_images else "")
    )
    for command in commands:
        try:
            run_command(command, install_dir, show_output=False)
        except subprocess.CalledProcessError as err:
            errors.append(str(err))

    # Attempt to remove all the config files.
    LOG.info("Removing config files.")
    for config_file in CONFIG_FILES:
        file_path = os.path.join(install_dir, config_file)
        if not os.path.exists(file_path):
            LOG.warning(
                "Config file %r not found. Skipping removal.", file_path
            )
            continue
        LOG.debug("Removing config file: %r", file_path)
        try:
            os.remove(file_path)
        except OSError as err:
            errors.append(f"Failed to remove config file {file_path!r}: {err}")
            LOG.exception(errors[-1])

    if errors:
        message = f"Could not remove all installed artifacts: {errors}"
        LOG.error(message)
        raise OSError(message)
    LOG.info("Removal complete.")


def build_parser() -> argparse.ArgumentParser:
    "Create a command line parser for managing a standalone regscale instance."

    parser = argparse.ArgumentParser(
        description="Manage a standalone instance of Regscale",
    )
    parser.add_argument(
        "command",
        choices=[
            "setup",
            "start",
            "stop",
            "status",
            "update",
            "remove",
            "remove-all",
        ],
        help="What action to take with the standalone RegScale instance",
    )
    parser.add_argument(
        "install_dir",
        default=os.path.curdir,
        nargs="?",
        help="The directory the standalone RegScale instance was setup in. "
        "Defaults to the current directory",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help=(
            "increase level of feedback output. Use -vv for even more detail. "
            "Log level defaults to "
            + repr(logging.getLevelName(DEFAULT_LOG_LEVEL))
        ),
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="count",
        default=0,
        help="decrease level of feedback output. Use -qq for even less detail",
    )
    parser.add_argument(
        "--version",
        help=(
            "display the program name and version number "
            f"(v{__version__}), and then exit"
        ),
    )
    return parser


def configure_logging(verbose: int, quiet: int) -> None:
    "Configure logging based on the number of verbose and quiet flags given."
    default_index = _LOG_LEVELS.index(DEFAULT_LOG_LEVEL)
    verbosity = default_index + verbose - quiet
    verbosity = min(verbosity, len(_LOG_LEVELS) - 1)
    verbosity = max(verbosity, 0)
    logging.basicConfig(
        level=_LOG_LEVELS[verbosity],
        format="{asctime} [{levelname}] standalone_regscale.py - {message}",
        style="{",
    )


def open_browser_after_startup() -> None:
    """Open a browser tab to the standalone RegScale instance once it is up."""
    LOG.info("Waiting for the instance to finish starting up.")
    started = False
    while not started:
        try:
            result = run_command("docker logs atlas", show_output=False)
        except subprocess.CalledProcessError:
            LOG.exception(
                "Error running command `docker logs atlas` to check the "
                "startup status:",
            )
            LOG.exception("Skipping opening web browser tab to: http://localhost")
            raise
        started = (
            "RegScale startup completed." in result.stdout
            if result.stdout
            else False
        )
        if result.stderr and "Unhandled exception" in result.stderr:
            message = "Unexpected error with standalone RegScale instance startup."
            LOG.error(message)
            if result.stdout:
                LOG.error("Showing application output:\n%s", result.stdout)
            LOG.error("Showing application errors:\n%s", result.stderr)
            raise OSError(message)
        if not started:
            time.sleep(_STARTUP_CHECK_DELAY_SECS)
    LOG.info(
        "Opening new web browser tab to standalone RegScale instance at: %r",
        _STANDALONE_URL,
    )
    webbrowser.open_new_tab(_STANDALONE_URL)

def run_function_cmd(command: str, install_dir: str) -> int:
    """Run the appropriate function for the given command."""
    if command == "setup":
        setup(install_dir)
    elif command == "remove":
        remove(install_dir)
    elif command == "remove-all":
        remove(install_dir, remove_images=True)
    elif command == "update":
        update_images(install_dir)
    else:
        LOG.critical("Unknown command: %r", command)
        return 1
    return 0


def main(raw_args: list[str] = sys.argv[1:]) -> int:
    "Run the standalone RegScale manager from the command line."

    # Handle the command line arguments.
    parser = build_parser()
    # Argparse requires a valid command choice or it won't show help, so we do
    # it instead if needed.
    if "--help" in raw_args or "-h" in raw_args:
        parser.print_help()
        return 0

    if "--version" in raw_args:
        print(f"{os.path.basename(sys.argv[0])} {__version__}")
        return 0

    args = build_parser().parse_args(raw_args)
    configure_logging(args.verbose, args.quiet)
    LOG.debug("Command line arguments: %r", args)
    args.install_dir = os.path.abspath(args.install_dir)
    LOG.debug("Using absolute path: %r", args.install_dir)

    check_requirements(args.install_dir)

    try:
        # Execute any function based command.
        if args.command not in _DOCKER_CMDS:
            return run_function_cmd(args.command, args.install_dir)

        # Otherwise, process the docker based command.
        docker_compose_file = os.path.join(
            args.install_dir, DOCKER_COMPOSE_YAML_FILE
        )

        # Make sure we are setup before we run start.
        if args.command == "start" and not os.path.exists(docker_compose_file):
            LOG.info(
                "Docker compose file %r not found. Running setup first.",
                docker_compose_file,
            )
            setup(args.install_dir)

        # Run the docker command.
        command, desc = _DOCKER_CMDS[args.command]
        LOG.info(desc, args.install_dir)
        run_command(
            command.format(
                compose_file=os.path.join(
                    args.install_dir, DOCKER_COMPOSE_YAML_FILE
                )
            ),
            args.install_dir,
        )
        LOG.debug("Command complete.")

        # If we started the application, show it in the browser.
        if args.command == "start":
            open_browser_after_startup()

        return 0
    except (OSError, subprocess.CalledProcessError):
        return 1
    except Exception:
        LOG.exception("Unknown exception occurred.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
