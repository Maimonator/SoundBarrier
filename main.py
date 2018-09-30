import argparse
import os
from soundbarrier import SoundBarrierItem
from glob import glob
from itertools import chain
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)


def get_song_info(args):
    for path in args.input:
        with SoundBarrierItem(path, args.output) as sb:
            if args.bpm:
                print "{} bpm is {}".format(sb.filename, sb.get_bpm())
            if args.graph:
                outputs = sb.get_song_graph()
                for output in outputs:
                    print "{} graph saved to \"{}\"".format(sb.filename,
                                                            output)
                    print "------------------"
            print "======================="


def compare_song(args):
    for path in args.input:
        with SoundBarrierItem(path, args.output) as sb1:
            with SoundBarrierItem(args.song, args.output) as sb2:
                print "Song score is {}".format(sb1.compare_to(sb2))


def flat_file_list(l):
    files = [glob(i) for i in l]
    return list(set(chain(*files)))


def main():
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        description="""
this program analyzes music woot woot.
""")

    parser.add_argument(
        "input", help="input file to analyze", nargs="+")
    parser.add_argument(
        "--output", "-o", help="output dir to write files to",
        default="generated")

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

    diff_parser = subparsers.add_parser(
        'diff',
        help="gives a score between 0 to 1 on how similar the songs are")

    diff_parser.add_argument(
        '-s',
        '--song',
        help="song path to compare to", required=True)

    diff_parser.set_defaults(do=compare_song)
    args = parser.parse_args()
    args.input = flat_file_list(args.input)
    args.do(args)


if __name__ == "__main__":
    main()
