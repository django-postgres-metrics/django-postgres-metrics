#!/usr/bin/env python

import json
import os
import sys
from typing import List, Optional, Tuple
from urllib.request import Request, urlopen

GHA_USER = "github-actions[bot]"
BODY_PREFIX = "<!-- SCREENSHOT POST -->\n"
BASE_URL = (
    "https://api.github.com/repos/django-postgres-metrics/django-postgres-metrics"
)


def find_screenshot_comment_id(pr_id: str) -> Optional[int]:
    with urlopen(f"{BASE_URL}/issues/{pr_id}/comments") as r:
        comments = json.loads(r.read().decode())

    for comment in comments:
        if comment["user"]["login"] == GHA_USER and comment["body"].startswith(
            BODY_PREFIX
        ):
            return comment["id"]
    return None


def get_image_urls(filename: str) -> List[Tuple[str, str, str]]:
    with open(filename) as fp:
        images = json.load(fp)
    return [
        (image["filename"], image["thumbnail_url"], image["image_url"])
        for image in sorted(images, key=lambda i: i["filename"])
    ]


def format_img(img: Tuple[str, str, str]):
    return f"| [{img[0]}]({img[2]}) " f"| [![]({img[1]})]({img[2]}) " "| "


def format_body(imgs: List[Tuple[str, str, str]]) -> str:
    rows = [
        BODY_PREFIX,
        "| Metric name | Screenshot |   | Metric name | Screenshot |",
        "| ----------- | ---------- | - | ----------- | ---------- |",
    ]

    rows.extend(
        [
            (
                format_img(imgs[i])
                + (format_img(imgs[i + 1]) if i < len(imgs) - 1 else "")
            )
            for i in range(0, len(imgs), 2)
        ]
    )
    return "\n".join(rows)


def update_comment(comment_id: int, body: str, token: str) -> None:
    req = Request(
        f"{BASE_URL}/issues/comments/{comment_id}",
        data=json.dumps({"body": body}).encode(),
        headers={
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    with urlopen(req):
        pass


def write_comment(pr_id: str, body: str, token: str) -> None:
    req = Request(
        f"{BASE_URL}/issues/{pr_id}/comments",
        data=json.dumps({"body": body}).encode(),
        headers={
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    with urlopen(req):
        pass


if __name__ == "__main__":
    pr_id = int(sys.argv[1])
    comment_id = find_screenshot_comment_id(pr_id)
    images = get_image_urls(sys.argv[2])
    body = format_body(images)
    token = os.environ["GITHUB_TOKEN"]
    if comment_id:
        update_comment(comment_id, body, token)
    else:
        write_comment(pr_id, body, token)
