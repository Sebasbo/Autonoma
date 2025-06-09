import os


class FileManager:
    """
    Manages file operations within a specified base directory.
    Provides methods for reading and writing files, ensuring that
    necessary subdirectories are created.
    """
    def __init__(self, base_dir: str = "output") -> None:
        """
        Initializes the FileManager.

        Args:
            base_dir: The base directory relative to which all file operations
                      will be performed. Defaults to "output".
        """
        self.base_dir: str = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def write_file(self, file_path: str, content: str) -> None:
        """
        Writes content to a file within the base directory.
        Creates necessary subdirectories if they don't exist.

        Args:
            file_path: The path to the file, relative to the base directory.
            content: The string content to write to the file.
        """
        full_path: str = os.path.join(self.base_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

    def read_file(self, file_path: str) -> str:
        """
        Reads content from a file within the base directory.

        Args:
            file_path: The path to the file, relative to the base directory.

        Returns:
            The content of the file as a string.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        full_path: str = os.path.join(self.base_dir, file_path)
        with open(full_path, "r") as f:
            return f.read()
