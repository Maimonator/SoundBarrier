import argparse
import os
from soundbarrier import SoundBarrierItem
from videobarrier import VideoBarrier
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
                sb.get_song_graph(args.graph)


def compare_song(args):
    with SoundBarrierItem(args.song, args.output) as sb2:
        for path in args.input:
            with SoundBarrierItem(path, args.output) as sb1:
                print "====================="
                score, time_diff = sb1.compare_to(sb2)
                print """
{}: For a song score of {}, song should start at {}(s) """.format(
                    sb1.filename
                    ,score,
                    time_diff)
                print "---------------------"


def create_video(args):
    with SoundBarrierItem(args.song, args.output) as sb2:
        for path in args.input:
            with SoundBarrierItem(path, args.output) as sb1:
                print "====================="
                score, time_diff = sb1.compare_to(sb2)
                print """
{} For a song score of {}, song should start at {}(s) """.format(sb2.filename,
                    score,
                    time_diff)
                print "---------------------"

    with VideoBarrier(args.clip, args.output, args.song) as vb:
        vb.set_audio(time_diff, time_diff + args.duration)
        vb.save(args.clip_start_time, args.duration)


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

    # Info parser
    info_parser = subparsers.add_parser(
        'info',
        help="return info on the song analyzed")

    info_parser.add_argument(
        '--bpm',
        help="print the BPM estimate of a song",
        action="store_true")

    info_parser.add_argument(
        '--graph',
        help="output PNG files containing different graphs accepts: 'harm'",
        nargs="+",
        choices=['amp', 'chroma', 'harm', 'perc'],
        default=['amp'])

    info_parser.set_defaults(do=get_song_info)

    # Diff Parser
    diff_parser = subparsers.add_parser(
        'diff',
        help="gives a score between 0 to 1 on how similar the songs are")

    diff_parser.add_argument(
        '-s',
        '--song',
        help="song path to compare to", required=True)

    diff_parser.set_defaults(do=compare_song)

    # Video Parser
    video_parser = subparsers.add_parser(
        'video',
        help="Edits a song into another video")

    video_parser.add_argument(
        '-s',
        '--song',
        help="song path to edit into the clip", required=True)

    video_parser.add_argument(
        '--clip',
        help="video clip path to edit", required=True)

    video_parser.add_argument(
        '--clip-start-time',
        help="where to start the clip in seconds",
        type=float,
        default=0)

    video_parser.add_argument(
        '-d',
        '--duration',
        help="clip duration in seconds",
        type=float,
        default=60.0)

    video_parser.set_defaults(do=create_video)

    args = parser.parse_args()
    args.input = flat_file_list(args.input)
    args.do(args)


if __name__ == "__main__":
    main()
