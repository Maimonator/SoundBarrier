import argparse
from soundbarrier import SoundBarrier


def get_song_info(args):
    with SoundBarrier(args.input) as sb:
        print "Song bpm is {}".format(sb.get_bpm())
        sb.get_song_graph()


def main():
    parser = argparse.ArgumentParser(
        description="This program analyzes music woot woot")
    parser.add_argument(
        "--input", "-i", help="The input file to analyze", required=True)
    parser.add_argument(
        "--output", "-o", help="Output dir where to write the files")

    args = parser.parse_args()
    get_song_info(args)


if __name__ == "__main__":
    main()
