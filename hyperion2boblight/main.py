#! /usr/bin/env python3
"""
Entry point to run a Hyperion2Boblight server
"""

import logging
import argparse
import threading

from hyperion2boblight import PriorityList, BoblightClient, HyperionServer

def main():
    """ Main function """
    # Start by handling the command line arguments
    arg_parser = argparse.ArgumentParser(
        prog="Hyperion2Boblight",
        description="A server to command a boblight server with a hyperion client",
        add_help=True,
        allow_abbrev=True
    )
    arg_parser.add_argument(
        "--listening-address", "-A",
        dest="listening_address",
        help="Address to bind the server to (default: %(default)s)",
        default="localhost"
    )
    arg_parser.add_argument(
        "--listening-port", "-P",
        dest="listening_port",
        help="Port to bind the server to (default: %(default)s)",
        default=19444,
        type=int
    )
    arg_parser.add_argument(
        "--boblight-address", "-a",
        dest="boblight_address",
        help="Address of the boblight server to command (default: %(default)s)",
        default="localhost"
    )
    arg_parser.add_argument(
        "--boblight-port", "-p",
        dest="boblight_port",
        help="Port that boblight server is listening (default: %(default)s)",
        default=19445,
        type=int
    )
    arg_parser.add_argument(
        "--debug", "-d",
        help="Print debug messages",
        action="store_const",
        default=logging.INFO,
        const=logging.DEBUG
    )
    options = arg_parser.parse_args()

    # Configure the logging process
    logging.basicConfig(
        level=options.debug,
        format="## %(levelname)s ## %(threadName)s ## %(message)s"
    )
    logging.info("Options parsed")
    logging.debug("Debug output activated")

    # Build base components
    priority_list = PriorityList()
    client = BoblightClient(
        (options.boblight_address, options.boblight_port),
        priority_list
    )
    server = HyperionServer(
        (options.listening_address, options.listening_port),
        priority_list
    )

    # Create threads
    client_thread = threading.Thread(target=client.run)
    server_thread = threading.Thread(target=server.serve_forever)

    # Launch threads
    client_thread.start()
    server_thread.start()

    try:
        server_thread.join()
        client_thread.join()
    except KeyboardInterrupt:
        logging.info("^C received. Closing server...")
        server.shutdown()
        server.server_close()

    logging.info('Exiting')

if __name__ == "__main__":
    main()
