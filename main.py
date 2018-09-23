import argparse
import os
from soundbarrier import SoundBarrier


def get_song_info(args):
    with SoundBarrier(args.input) as sb:
        if args.bpm:
            print "Song bpm is {}".format(sb.get_bpm())
        if args.graph:
            print "Graph was saved to \"{}\"".format(sb.get_song_graph())


def main():
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        description="""
this program analyzes music woot woot.
""")

    parser.add_argument(
        "--input", "-i", help="input file to analyze", required=True)
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
        help="output SVG file containing different graphs",
        action="store_true")

    info_parser.set_defaults(do=get_song_info)

    args = parser.parse_args()
    args.do(args)


if __name__ == "__main__":
    main()
