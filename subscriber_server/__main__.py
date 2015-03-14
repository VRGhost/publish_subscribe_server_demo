"""Entry point for the subscriber_server"""

import subscriber_server

if __name__ == "__main__":
    args = subscriber_server.main.get_arg_parser().parse_args()
    subscriber_server.main.main(args)
