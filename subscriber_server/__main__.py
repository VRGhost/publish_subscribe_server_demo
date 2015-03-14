"""Entry point for the subscriber_server"""

import subscriber_server.main as main

if __name__ == "__main__":
    args = main.get_arg_parser().parse_args()
    main.main(args)
