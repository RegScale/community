# If a password error occurs, you need to prune the atlas volumes that may be stranded "docker volume prune "

import argparse
from .standalone import check_docker, deploy_RegScale
from .teardown import teardown

#=======================================================================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action', type=str,
        help='The action to be requested: "install", or "teardown".'
    )
    args = parser.parse_args()

    if args.action == 'install':
        deploy_RegScale()
    elif args.action == 'teardown':
        teardown()
    else:
        print('\n\nInvalid command. Options are: \n\t"regscale-standalone install" - run installation script '
              '\n\t"regscale-standalone teardown" - purge files from an existing install.\n\n')

if __name__ == "__main__":
    main()