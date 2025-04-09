from aws_s3_helper.interface import S3Interface
from aws_s3_helper.s3_with_logs import S3WithLogs
from aws_s3_helper.s3_without_logs import S3WithoutLogs


class S3(S3Interface):
    def __init__(self, aws_region: str, aws_access_key_id: str = None, aws_secret_access_key: str = None, logging: bool = False):
        """
        AWS S3 client.

        Args:
            aws_access_key_id (str): The AWS access key.
            aws_secret_access_key (str, optional): The AWS secret access key.
            aws_region (str, optional): The AWS region.
            logging (bool, optional): If True, the client will show logs.

        Raises:
            Exception: If the credentials or region are not well defined.
        """
        self.__client = (
            S3WithLogs(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_region=aws_region,
            )
            if logging
            else S3WithoutLogs(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_region=aws_region,
            )
        )

    # ------------------------- List functions ---------------------------

    def list_buckets(self) -> list[str]:
        return self.__client.list_buckets()

    def list(self, bucket_name: str, prefix: str = "") -> dict[str, list[str]]:
        return self.__client.list(bucket_name, prefix)

    # ------------------------- File functions ---------------------------

    def read_file(self, bucket_name: str, s3_path: str, format: str | None = None) -> str:
        return self.__client.read_file(bucket_name, s3_path, format)

    def rename_file(self, bucket_name: str, old_s3_path: str, new_s3_path: str) -> None:
        self.__client.rename_file(bucket_name, old_s3_path, new_s3_path)

    def download_file(self, bucket_name: str, s3_path: str, local_path: str) -> None:
        self.__client.download_file(bucket_name, s3_path, local_path)

    def get_presigned_url_file(self, bucket_name: str, s3_path: str) -> str:
        return self.__client.get_presigned_url_file(bucket_name, s3_path)

    def upload_file(self, bucket_name: str, file_path: str, s3_path: str) -> None:
        self.__client.upload_file(bucket_name, file_path, s3_path)

    def delete_file(self, bucket_name: str, s3_path: str) -> None:
        self.__client.delete_file(bucket_name, s3_path)

    # ------------------------- Folder functions ---------------------------

    def download_folder(self, bucket_name: str, s3_path: str, local_path: str) -> None:
        self.__client.download_folder(bucket_name, s3_path, local_path)

    def upload_folder(self, bucket_name: str, folder_path: str, s3_path: str) -> None:
        self.__client.upload_folder(bucket_name, folder_path, s3_path)

    def delete_folder(self, bucket_name: str, s3_path: str) -> None:
        self.__client.delete_folder(bucket_name, s3_path)

    def rename_folder(self, bucket_name: str, old_s3_path: str, new_s3_path: str) -> None:
        self.__client.rename_folder(bucket_name, old_s3_path, new_s3_path)

    # ------------------------- Buckets functions ---------------------------

    def create_bucket(self, bucket_name: str) -> None:
        self.__client.create_bucket(bucket_name)

    def delete_bucket(self, bucket_name: str) -> None:
        self.__client.delete_bucket(bucket_name)

    def rename_bucket(self, old_bucket_name: str, new_bucket_name: str) -> None:
        self.__client.rename_bucket(old_bucket_name, new_bucket_name)
