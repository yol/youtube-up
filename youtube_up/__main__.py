import argparse
import datetime
import json
from enum import Enum

import tqdm

from .metadata import *
from .uploader import YTUploaderSession


def main():
    parser = argparse.ArgumentParser(
        prog="youtube-up",
        description="Upload videos to YouTube using the internal YouTube API",
    )
    subparsers = parser.add_subparsers(help="commands", dest="command")

    json_parser = subparsers.add_parser("json")
    json_parser.add_argument(
        "filename",
        help=".json file specifying videos to upload. File should"
        "be an array of objects with 'file' and 'metadata' keys where 'file' "
        "is a path to a video file and 'metadata' is structured as the Metadata"
        "class",
    )
    json_parser.add_argument(
        "--cookies_file", help="Path to Netscape cookies.txt file", required=True
    )

    video_parser = subparsers.add_parser("video")
    video_parser.add_argument("filename", help="Video file to upload")
    video_parser.add_argument(
        "--cookies_file", help="Path to Netscape cookies.txt file", required=True
    )
    video_parser.add_argument("--title", help="Title. Max length 100", required=True)
    video_parser.add_argument(
        "--description", help="Description. Max length 5000", default=""
    )
    video_parser.add_argument(
        "--privacy", help="Privacy", type=PrivacyEnum.__getattr__, required=True
    )
    video_parser.add_argument(
        "--made_for_kids",
        help="Made for kids. If true comments will be disabled",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    video_parser.add_argument("--tags", nargs="+", help="List of tags")
    video_parser.add_argument(
        "--scheduled_upload",
        help="Date to make upload public, in ISO format. If set, video will be set to private until the"
        " date, unless video is a premiere in which case it will be set to public. Video will not be a"
        " premiere unless both premiere_countdown_duration and premiere_theme are set",
        type=datetime.datetime.fromisoformat,
    )
    video_parser.add_argument(
        "--premiere_countdown_duration",
        help="Duration of premiere countdown in seconds",
        type=PremiereDurationEnum,
    )
    video_parser.add_argument(
        "--premiere_theme",
        help="Theme of premiere countdown",
        type=PremiereThemeEnum.__getattr__,
    )
    video_parser.add_argument(
        "--playlist_ids",
        nargs="+",
        help="List of existing playlist IDs to add video to",
    )
    video_parser.add_argument("--thumbnail", help="Path to thumbnail file to upload")
    video_parser.add_argument(
        "--publish_to_feed",
        help="Whether to notify subscribers",
        action=argparse.BooleanOptionalAction,
    )
    video_parser.add_argument(
        "--category",
        help="Category. Category-specific metadata is not supported yet",
        type=CategoryEnum.__getattr__,
    )
    video_parser.add_argument(
        "--auto_chapter",
        help="Whether to use automatic video chapters",
        action=argparse.BooleanOptionalAction,
    )
    video_parser.add_argument(
        "--auto_places",
        help="Whether to use automatic places",
        action=argparse.BooleanOptionalAction,
    )
    video_parser.add_argument(
        "--auto_concepts",
        help="Whether to use automatic concepts",
        action=argparse.BooleanOptionalAction,
    )
    video_parser.add_argument(
        "--has_product_placement",
        help="Whether video has product placement",
        action=argparse.BooleanOptionalAction,
    )
    video_parser.add_argument(
        "--show_product_placement_overlay",
        help="Whether to show product placement overlay",
        action=argparse.BooleanOptionalAction,
    )
    video_parser.add_argument(
        "--recorded_date",
        help="Day, month, and year that video was recorded, in ISO format",
        type=datetime.date.fromisoformat,
    )
    video_parser.add_argument(
        "--restricted_to_over_18",
        help="Whether video is age restricted",
        action=argparse.BooleanOptionalAction,
    )
    video_parser.add_argument(
        "--audio_language",
        help="Language of audio. If uploading captions this must be set",
        action=argparse.BooleanOptionalAction,
    )
    video_parser.add_argument(
        "--license",
        help="License",
        type=LicenseEnum.__getattr__,
    )
    video_parser.add_argument(
        "--allow_comments",
        help="Whether to allow comments",
        action=argparse.BooleanOptionalAction,
    )
    video_parser.add_argument(
        "--allow_comments_mode",
        help="Comment filtering mode",
        type=AllowCommentsEnum.__getattr__,
    )
    video_parser.add_argument(
        "--can_view_ratings",
        help="Whether video likes/dislikes can be seen",
        action=argparse.BooleanOptionalAction,
    )
    video_parser.add_argument(
        "--comments_sort_order",
        help="Default comment sort order",
        type=CommentsSortOrderEnum.__getattr__,
    )
    video_parser.add_argument(
        "--allow_embedding",
        help="Whether to allow embedding on 3rd party sites",
        action=argparse.BooleanOptionalAction,
    )

    args = parser.parse_args()

    uploader = YTUploaderSession.from_cookies_txt(args.cookies_file)

    if args.command == "json":
        with open(args.filename, "r") as f:
            data = json.load(f)
        with tqdm.tqdm(total=100 * len(data)) as pbar:
            for i, video in enumerate(data):

                def callback(step: str, prog: int):
                    pbar.n = 100 * i + prog
                    pbar.update()

                uploader.upload(
                    video["file"], Metadata.from_dict(video["metadata"]), callback
                )
    else:
        args_dict = vars(args)
        args_dict.pop("cookies_file")
        args_dict.pop("command")
        video_file = args_dict.pop("filename")
        metadata = Metadata.from_dict(args_dict)

        with tqdm.tqdm(total=100) as pbar:

            def callback(step: str, prog: int):
                pbar.n = prog
                pbar.update()

            uploader.upload(video_file, metadata, callback)


if __name__ == "__main__":
    main()