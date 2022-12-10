#! /usr/bin/env python

import argparse
import sys

from rec_app import app

def graceful_exit(msg):
    """Gracefully exit program. Prints error to stderr
    """
    print(msg, file=sys.stderr)
    sys.exit(1)

def get_arguments():
    """
    Sets up acceptable command line flags and help messsage.
    """

    parser = argparse.ArgumentParser(description="The registrar application")

    parser.add_argument(
        "port",
        help="the port at which the server should listen",
    )

    args = parser.parse_args()

    port = args.port

    # check it's a number
    if not port.isnumeric():
        graceful_exit("Port number contains nonnumeric.")

    port = int(port)
    # check it's in the range of [0, 65535]
    if port < 0 or port > 65535:
        graceful_exit(
            f"The given port number, {port}, is not in the range of [0, 65535]"
        )

    return port

def main():
    """Runs main.
    """
    port = get_arguments()

    try:
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as ex:
        graceful_exit(ex)


if __name__ == "__main__":
    sys.exit(main())
