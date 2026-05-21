from time import time
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.timezone import now
from django.conf import settings


def _upload_path(model, filetype, filename):
    """
    base function to generate upload path for media files to prevent duplicate
    """
    path = f"{filetype}/{model._meta.model_name}/{timezone.localdate()}"
    ext = filename.rsplit(".", 1)
    filename = slugify(f"{int(time())}-{ext[0]}")
    
    if len(ext) > 1:
        filename += "." + ext[-1]

    return f"{path}/{filename}"


def get_image_upload_path(model, filename):
    """generate upload path for images to prevent duplicate"""
    return _upload_path(model, "images", filename)


def get_video_upload_path(model, filename):
    """generate upload path for videos to prevent duplicate"""
    return _upload_path(model, "videos", filename)


def get_audio_upload_path(model, filename):
    """generate audio path for audio to prevent duplicate"""
    return _upload_path(model, "audio", filename)


def get_document_upload_path(model, filename):
    """generate document path for audio to prevent duplicate"""
    return _upload_path(model,f"documents/{now().date()}", filename)


def get_image_url(model, attr, image_path='images/no-image-icon.png'):
    """return image if it exists otherwise use a default"""
    obj = getattr(model, attr, '')

    if obj:
        return obj.url

    return f"{settings.STATIC_URL}{image_path}"

