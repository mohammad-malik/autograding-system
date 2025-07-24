import os
import uuid
from typing import BinaryIO, Optional, Tuple

# from dotenv import load_dotenv  # redundant
# load_dotenv()  # redundant

from ..config import get_settings
from ..models.database_utils import supabase


class StorageClient:
    """Client for file storage operations."""

    BUCKET_TEXTBOOKS = get_settings().bucket_textbooks
    BUCKET_QUIZZES = get_settings().bucket_quizzes
    BUCKET_SUBMISSIONS = get_settings().bucket_submissions
    BUCKET_REPORTS = get_settings().bucket_reports
    BUCKET_SLIDES = get_settings().bucket_slides

    @staticmethod
    async def init_storage():
        """Initialize storage buckets."""
        # Create buckets if they don't exist
        for bucket in [
            StorageClient.BUCKET_TEXTBOOKS,
            StorageClient.BUCKET_QUIZZES,
            StorageClient.BUCKET_SUBMISSIONS,
            StorageClient.BUCKET_REPORTS,
            StorageClient.BUCKET_SLIDES,
        ]:
            try:
                supabase.storage.get_bucket(bucket)
            except:
                supabase.storage.create_bucket(bucket, {"public": False})

    @staticmethod
    async def upload_file(
        file_content: bytes, bucket: str, file_path: str
    ) -> Tuple[str, str]:
        """Upload file to storage."""
        # Ensure buckets exist
        await StorageClient.init_storage()

        # Upload file
        supabase.storage.from_(bucket).upload(
            file_path,
            file_content,
            {"content-type": "application/octet-stream"},
        )

        # Get file URL
        file_url = supabase.storage.from_(bucket).get_public_url(file_path)

        return file_path, file_url

    @staticmethod
    async def download_file(bucket: str, file_path: str) -> bytes:
        """Download file from storage."""
        # Get file
        response = supabase.storage.from_(bucket).download(file_path)

        return response

    @staticmethod
    async def delete_file(bucket: str, file_path: str) -> None:
        """Delete file from storage."""
        supabase.storage.from_(bucket).remove([file_path])

    @staticmethod
    async def upload_textbook(
        file_content: bytes, file_name: str, user_id: str
    ) -> Tuple[str, str]:
        """Upload textbook file."""
        # Generate unique file path
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file_name)[1]
        file_path = f"{user_id}/{file_id}{file_ext}"

        # Upload file
        return await StorageClient.upload_file(
            file_content, StorageClient.BUCKET_TEXTBOOKS, file_path
        )

    @staticmethod
    async def upload_quiz_pdf(
        file_content: bytes, file_name: str, user_id: str, quiz_id: str
    ) -> Tuple[str, str]:
        """Upload quiz submission PDF."""
        # Generate unique file path
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file_name)[1]
        file_path = f"{user_id}/{quiz_id}/{file_id}{file_ext}"

        # Upload file
        return await StorageClient.upload_file(
            file_content, StorageClient.BUCKET_SUBMISSIONS, file_path
        )

    @staticmethod
    async def upload_generated_file(
        file_content: bytes,
        file_name: str,
        user_id: str,
        bucket: str,
    ) -> Tuple[str, str]:
        """Upload generated file (slides, quiz, report)."""
        # Generate unique file path
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file_name)[1]
        file_path = f"{user_id}/{file_id}{file_ext}"

        # Upload file
        return await StorageClient.upload_file(file_content, bucket, file_path) 