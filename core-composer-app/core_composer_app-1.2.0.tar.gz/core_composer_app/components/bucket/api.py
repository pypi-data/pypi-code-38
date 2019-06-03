"""Bucket api
"""
from core_composer_app.components.bucket.models import Bucket
from core_main_app.commons.exceptions import ApiError

import random


def get_by_id(bucket_id):
    """Return a bucket given its id.

    Args:
        bucket_id:

    Returns:

    """
    return Bucket.get_by_id(bucket_id)


def upsert(bucket):
    """Save or update a bucket.

    Args:
        bucket:

    Returns:

    """
    # get list of colors already present
    existing_colors = Bucket.get_colors()
    # set a color if not set
    if bucket.color is None:
        # get a unique color
        color = _get_random_hex_color()
        while color in existing_colors:
            color = _get_random_hex_color()

        bucket.color = color

    return bucket.save_object()


def get_all():
    """Return all buckets.

    Returns:

    """
    return Bucket.get_all()


def delete(bucket):
    """Delete a bucket.

    Args:
        bucket:

    Returns:

    """
    bucket.delete()


def _get_random_hex_color():
    """Return a random hexa color string.

    Returns:

    """
    return '#' + ''.join([random.choice('0123456789ABCDEF') for x in range(6)])


def add_type_to_buckets(version_manager, list_bucket_ids):
    """Add type version manager to buckets.

    Args:
        version_manager:
        list_bucket_ids:

    Returns:

    """
    if list_bucket_ids is None:
        return

    # Iterate through list of bucket ids
    for bucket_id in list_bucket_ids:
        try:
            # get the bucket using its id
            bucket = get_by_id(bucket_id)
        except:
            raise ApiError("No bucket found with the given id.")

        # add type to bucket
        bucket.types.append(version_manager)
        # update bucket
        upsert(bucket)


def update_type_buckets(version_manager, list_bucket_ids):
    """Remove type from current buckets and puts them in new list.

    Args:
        version_manager:
        list_bucket_ids:

    Returns:

    """
    # remove types from current buckets
    remove_type_from_buckets(version_manager)
    # add types to new list of buckets
    add_type_to_buckets(version_manager, list_bucket_ids)


def remove_type_from_buckets(version_manager):
    """Remove the type from all the buckets.

    Args:
        version_manager:

    Returns:

    """
    buckets = get_all()

    # Iterate through all buckets
    for bucket in buckets:
        # if type in bucket
        if version_manager in bucket.types:
            # remove type from the bucket
            bucket.types.remove(version_manager)
            # update bucket
            upsert(bucket)
