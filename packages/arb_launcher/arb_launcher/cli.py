import argparse

from arb_launcher.launcher import launch_detached


def main():
    parser = argparse.ArgumentParser(description="Launch a program and detach")

    parser.add_argument("--stdout", help="File to redirect stdout")
    parser.add_argument("--stderr", help="File to redirect stderr")
    parser.add_argument("command", help="Program to launch and detach")

    args, unknownargs = parser.parse_known_args()

    launch_detached(args.command, unknownargs, args.stdout, args.stderr)


if __name__ == "__main__":
    main()
