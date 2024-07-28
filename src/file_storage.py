import abc
import os


class FileStorage(abc.ABC):
    """
    Abstract class for file storage
    """

    @abc.abstractmethod
    def save_file(self, file_name, data) -> str:
        pass

    @abc.abstractmethod
    def get_file(self, file_name):
        pass

    @abc.abstractmethod
    def delete_file(self, file_name):
        pass


class LocalFileStorage(FileStorage):
    def __init__(self, storage_path):
        self.storage_path = storage_path

    def save_file(self, file_name, data) -> str:
        file_path = self._get_file_path(file_name)
        with open(file_path, "wb") as file:
            file.write(data)
            return file_path

    def get_file(self, file_name):
        file_path = self._get_file_path(file_name)
        with open(file_path, "rb") as file:
            return file.read()

    def delete_file(self, file_name):
        file_path = self._get_file_path(file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

    def _get_file_path(self, file_name):
        return os.path.join(self.storage_path, file_name)


file_storage: FileStorage = LocalFileStorage(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../file_storage"))
)
