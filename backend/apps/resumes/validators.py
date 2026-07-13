"""Secure upload validation for resume files.

Defence in depth — we do not trust the client-supplied filename or content-type:
1. extension allow-list,
2. size limit,
3. **magic-byte** sniffing of the actual bytes (PDF `%PDF`, DOCX = ZIP `PK\\x03\\x04`),
   so a `.exe` renamed to `.pdf` is rejected.
"""
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers

# Leading bytes that must be present for the claimed type.
_MAGIC = {
    "pdf": (b"%PDF",),
    # DOCX is an OOXML zip; all zips start with PK\x03\x04 (or empty/spanned variants).
    "docx": (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
}


def _extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def validate_resume_file(file: UploadedFile) -> str:
    """Validate an uploaded resume file. Returns the normalized file type
    ("pdf"/"docx"). Raises DRF ValidationError on any failure."""
    ext = _extension(file.name or "")
    allowed = settings.RESUME_ALLOWED_EXTENSIONS
    if ext not in allowed:
        raise serializers.ValidationError(
            f"Unsupported file type '.{ext}'. Allowed: {', '.join(allowed)}."
        )

    max_size = settings.RESUME_MAX_UPLOAD_SIZE
    if file.size is not None and file.size > max_size:
        mb = max_size / (1024 * 1024)
        raise serializers.ValidationError(f"File too large. Maximum size is {mb:.0f} MB.")
    if not file.size:
        raise serializers.ValidationError("Uploaded file is empty.")

    # Magic-byte check on the real content.
    head = file.read(8)
    file.seek(0)
    if not any(head.startswith(sig) for sig in _MAGIC[ext]):
        raise serializers.ValidationError(
            f"File content does not match a valid {ext.upper()} file."
        )
    return ext
