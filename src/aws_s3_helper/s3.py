import os

import boto3
from tqdm import tqdm

from .utils_checks import bucket_exists, s3_path_exists

class S3:
    def __init__(
        self, aws_access_key_id: str, aws_secret_access_key: str, aws_region: str
    ):
        """
        AWS S3 client.

        Args:
            aws_access_key_id: The AWS access key.
            aws_secret_access_key: The AWS secret access key.
            aws_region: The AWS region.

        Raises:
            Exception: If the credentials or region are not well defined.
        """
        try:
            self.__client = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region,
            )
        except Exception as e:
            raise Exception("--- The S3 configuration is not correct --- ERROR", e)

    def list(self, bucket_name: str, prefix: str = "") -> dict[str, list[str]]:
        """
        Lists folders and files in an AWS S3 bucket under a specific prefix.

        Args:
            bucket_name (str): The name of the S3 bucket.
            prefix (str, optional): The prefix used to filter the objects in the bucket.
                                    Default is an empty string.

        returns:
            dict: A dictionary with two lists:
                  - 'folders': Names of folders found under the prefix (without the prefix or trailing slash).
                  - 'files': Names of the files found under the prefix (without the prefix).
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if len(prefix) > 0 and not s3_path_exists(self.__client, bucket_name, prefix):
            raise Exception(
                f"The path '{prefix}' does not exist in the bucket '{bucket_name}'."
            )

        # Removes the leading slash from the prefix if it exists
        if prefix.startswith("/"):
            prefix = prefix[1:]

        paginator = self.__client.get_paginator("list_objects_v2")
        operation_parameters: dict[str, str] = {
            "Bucket": bucket_name,
            "Prefix": prefix,
            "Delimiter": "/",
        }

        files: list[str] = []
        folders: list[str] = []

        for page in paginator.paginate(**operation_parameters):
            folders.extend(
                [
                    f["Prefix"][len(prefix) :].rstrip("/")
                    for f in page.get("CommonPrefixes", [])
                ]
            )
            files.extend([f["Key"][len(prefix) :] for f in page.get("Contents", [])])

        return {"folders": folders, "files": files}

    def download_file(self, bucket_name: str, s3_path: str, local_path: str) -> None:
        """
        Download a file from an AWS S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_path (str): The path to the file in the bucket.
            local_path (str): The path where the downloaded file will be saved.
        """

        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not s3_path_exists(self.__client, bucket_name, s3_path):
            raise Exception(
                f"The file '{s3_path}' does not exist in the bucket '{bucket_name}'."
            )

        # Get file size in S3
        response = self.__client.head_object(Bucket=bucket_name, Key=s3_path)
        file_size = response["ContentLength"]

        # Configuring the progress bar
        with tqdm(
            total=file_size,
            unit="B",
            unit_scale=True,
            desc=os.path.basename(local_path),
        ) as progress_bar:

            def download_progress(bytes_transferred):
                progress_bar.update(bytes_transferred)

            self.__client.download_file(
                bucket_name, s3_path, local_path, Callback=download_progress
            )

    def download_folder(self, bucket_name: str, s3_path: str, local_path: str) -> None:
        """
        Download a folder from an AWS S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_path (str): The path to the folder in the bucket.
            local_path (str): The path where the downloaded folder will be saved.
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not s3_path_exists(self.__client, bucket_name, s3_path):
            raise Exception(
                f"The folder '{s3_path}' does not exist in the bucket '{bucket_name}'."
            )

        # Create the local folder if it does not exist
        os.makedirs(local_path, exist_ok=True)
        objects = self.list(bucket_name, s3_path)
        total_items = len(objects["files"]) + len(objects["folders"])

        with tqdm(
            total=total_items,
            desc=f"Downloading folder: {local_path}",
        ) as overall_progress_bar:
            for file in objects["files"]:
                local_file_path = os.path.join(local_path, file)
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                self.download_file(
                    bucket_name, os.path.join(s3_path, file), local_file_path
                )
                overall_progress_bar.update(1)

            for folder in objects["folders"]:
                self.download_folder(
                    bucket_name,
                    os.path.join(s3_path, folder) + "/",
                    os.path.join(local_path, folder) + "/",
                )
                overall_progress_bar.update(1)

    def read_file(self, bucket_name: str, s3_path: str) -> str:
        """
        Reads the contents of a file stored in an AWS S3 bucket without downloading it.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_path (str): The path to the file in the bucket.

        Returns:
            str: The contents of the file as a string.

        Raises:
            Exception: If the bucket or file does not exist.
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not s3_path_exists(self.__client, bucket_name, s3_path):
            raise Exception(
                f"The file '{s3_path}' does not exist in the bucket '{bucket_name}'."
            )

        response = self.__client.get_object(Bucket=bucket_name, Key=s3_path)
        content = response["Body"].read().decode("utf-8")
        return content

    def upload_file(self, bucket_name: str, file_path: str, s3_path: str) -> None:
        """
        Upload a file to an AWS S3 bucket with a progress bar, checking if the file exists locally.

        Args:
            bucket_name (str): The name of the S3 bucket.
            file_path (str): The local path of the file to upload.
            s3_path (str): The path in the bucket where the file will be saved.

        Raises:
            Exception: If the bucket does not exist or the local file is not found.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                f"The file '{file_path}' does not exist on the local file system."
            )

        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        file_size = os.path.getsize(file_path)
        progress_bar = tqdm(
            total=file_size, unit="B", unit_scale=True, desc=f"Uploading {file_path}"
        )

        def upload_progress(chunk):
            progress_bar.update(chunk)

        self.__client.upload_file(
            Filename=file_path,
            Bucket=bucket_name,
            Key=s3_path,
            Callback=upload_progress,
        )

        progress_bar.close()

    def upload_folder(self, bucket_name: str, folder_path: str, s3_path: str) -> None:
        """
        Upload an entire folder to an AWS S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            folder_path (str): The local path of the folder to upload.
            s3_path (str): The path in the bucket where the folder will be saved.

        Raises:
            Exception: If the bucket or local folder is not found.
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not os.path.isdir(folder_path):
            raise FileNotFoundError(
                f"The folder '{folder_path}' does not exist on the local file system."
            )

        # Listar todos los archivos y carpetas en el directorio local
        total_files = sum(len(files) for _, _, files in os.walk(folder_path))
        total_folders = sum(len(dirs) for _, dirs, _ in os.walk(folder_path))
        total_items = total_files + total_folders

        with tqdm(
            total=total_items,
            desc=f"Uploading folder: {folder_path}",
        ) as overall_progress_bar:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    local_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file_path, folder_path)
                    s3_file_path = os.path.join(s3_path, relative_path).replace(
                        "\\", "/"
                    )

                    self.upload_file(bucket_name, local_file_path, s3_file_path)
                    overall_progress_bar.update(1)

                for folder in dirs:
                    s3_folder_path = (
                        os.path.join(
                            s3_path,
                            os.path.relpath(os.path.join(root, folder), folder_path),
                        ).replace("\\", "/")
                        + "/"
                    )
                    self.__client.put_object(Bucket=bucket_name, Key=s3_folder_path)
                    overall_progress_bar.update(1)

    def delete_file(self, bucket_name: str, s3_path: str) -> None:
        """
        Deletes a file from an AWS S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_path (str): The path to the file in the bucket.

        Raises:
            Exception: If the bucket or file does not exist.
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not s3_path_exists(self.__client, bucket_name, s3_path):
            raise Exception(
                f"The file '{s3_path}' does not exist in the bucket '{bucket_name}'."
            )

        self.__client.delete_object(Bucket=bucket_name, Key=s3_path)

    def delete_folder(self, bucket_name: str, s3_path: str) -> None:
        """
        Deletes a folder and all its contents from an AWS S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_path (str): The path to the folder in the bucket.

        Raises:
            Exception: If the bucket or folder does not exist.
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not s3_path_exists(self.__client, bucket_name, s3_path):
            raise Exception(
                f"The folder '{s3_path}' does not exist in the bucket '{bucket_name}'."
            )

        objects = self.list(bucket_name, s3_path)
        total_items = len(objects["files"]) + len(objects["folders"])

        with tqdm(
            total=total_items,
            desc=f"Removing folder: {s3_path}",
        ) as overall_progress_bar:
            for file in objects["files"]:
                self.delete_file(bucket_name, os.path.join(s3_path, file))
                overall_progress_bar.update(1)

            for folder in objects["folders"]:
                self.delete_folder(bucket_name, os.path.join(s3_path, folder) + "/")
                overall_progress_bar.update(1)
