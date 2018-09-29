import argparse
import os
from soundbarrier import SoundBarrier


def get_song_info(args):
    for path in args.input:
        with SoundBarrier(path) as sb:
            if args.bpm:
                print "{} bpm is {}".format(sb.filename, sb.get_bpm())
            if args.graph:
                outputs = sb.get_song_graph()
                for output in outputs:
                    print "{} graph saved to \"{}\"".format(sb.filename,
                                                            output)
                    print "------------------"
            print "======================="


def main():
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        description="""
this program analyzes music woot woot.
""")

    parser.add_argument(
        "input", help="input file to analyze", nargs="+")
    parser.add_argument(
        "--output", "-o", help="output dir to write files to")

    subparsers = parser.add_subparsers()
    info_parser = subparsers.add_parser(
        'info',
        help="return info on the song analyzed")

    info_parser.add_argument(
        '--bpm',
        help="print the BPM estimate of a song",
        action="store_true")

    info_parser.add_argument(
        '--graph',
        help="output PNG files containing different graphs",
        action="store_true")

    info_parser.set_defaults(do=get_song_info)

    args = parser.parse_args()
    args.do(args)


if __name__ == "__main__":
    main()
