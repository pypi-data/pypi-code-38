import random
from datetime import timedelta, datetime, date, time
from pathlib import Path
from time import sleep

from pyvko.post import Post
from pyvko.pyvko import Pyvko
from pyvko.pyvko import PhotosUploader


def test_uploading(pyvko: Pyvko):
    test_group = pyvko.get_group("pyvko_test2")

    uploader = PhotosUploader(pyvko.api)

    photo_paths = [path for path in Path("test_photos").iterdir()]

    photos = [uploader.upload_to_wall(test_group.id, path) for path in photo_paths]

    post = Post(text="post w 2 img", attachments=photos)

    test_group.add_post(post)


def create_scheduled_posts():
    start_date = date.today() + timedelta(days=3)

    step = timedelta(days=8)

    for i in range(20):
        post_date = start_date + step * i
        post_time = time(
            hour=random.randint(8, 23),
            minute=random.randint(0, 59),
        )

        post_datetime = datetime.combine(post_date, post_time)

        print(post_datetime)

        post = Post(
            text=f"post {i}\n\n{post_datetime}",
            date=post_datetime
        )

        # test_group.add_post(post)


def main():
    pyvko = Pyvko()

    # test_uploading(pyvko)

    test_group = pyvko.get_group("pyvko_test2")

    scheduled = test_group.get_scheduled_posts()

    start_date = scheduled[0].date.date()

    step = timedelta(days=2)

    for i, post in enumerate(scheduled):
        new_post_date = start_date + step * i

        if post.date.date() == new_post_date:
            continue

        new_post_time = post.date.time()

        new_post_datetime = datetime.combine(new_post_date, new_post_time)

        post.date = new_post_datetime
        post.text += f"\n{step.days}: {new_post_datetime}"

        test_group.update_post(post)

        print(f"updated {post.id}")

        sleep(random.randint(10, 20))



    a = 7


if __name__ == '__main__':
    main()
