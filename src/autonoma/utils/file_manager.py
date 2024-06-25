import os


class FileManager:
    def __init__(self, base_dir="output"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def write_file(self, file_path, content):
        full_path = os.path.join(self.base_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

    def read_file(self, file_path):
        full_path = os.path.join(self.base_dir, file_path)
        with open(full_path, "r") as f:
            return f.read()
