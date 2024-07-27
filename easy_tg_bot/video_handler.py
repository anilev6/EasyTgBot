import aiofiles

from .mylogging import logger
from .file_handler import FileHandler


class VideoFileHandler(FileHandler):
    def __init__(self,prefix):
        self.prefix = prefix
        self.file_key = f"{prefix}_video"
        self.key_to_file_id = f"{prefix}_video_id"

    async def delete_file(self, file_path):
        if file_path is not None:
            try:
                await aiofiles.os.remove(file_path)
                logger.info(f"Successfully deleted video: {file_path}")
            except OSError as e:
                logger.error(f"Error deleting video {file_path}: {e.strerror}")


intro_video_handler = VideoFileHandler("intro")
