from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image


def process_profile_picture(uploaded_file, *, max_size=(400, 400), quality=75):
    """Resize and normalize profile uploads for Cloudinary-compatible storage."""
    uploaded_file.seek(0)
    image = Image.open(uploaded_file)
    image = image.convert("RGB")
    image.thumbnail(max_size, Image.Resampling.LANCZOS)

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=quality, optimize=True)
    buffer.seek(0)

    original_name = getattr(uploaded_file, "name", "profile.jpg") or "profile.jpg"
    stem = original_name.rsplit(".", 1)[0] or "profile"
    return InMemoryUploadedFile(
        buffer,
        "ImageField",
        f"{stem}.jpg",
        "image/jpeg",
        buffer.getbuffer().nbytes,
        None,
    )
