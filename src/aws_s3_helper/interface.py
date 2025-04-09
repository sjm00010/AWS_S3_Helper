from abc import ABC, abstractmethod

class S3Interface(ABC):
    """
    Interface for the S3 class.
    """

    @abstractmethod
    def list_buckets(self) -> list[str]:
        """
        Lists all the buckets in the AWS S3 account.

        Returns:
            list[str]: A list of bucket names.
            
        Raises:
            Exception: If there is an error listing the buckets.
        """
        ...

    @abstractmethod
    def list(self, bucket_name: str, prefix: str = "") -> dict[str, list[str]]:
        """
        Lists folders and files in an AWS S3 bucket under a specific prefix.

        Args:
            bucket_name (str): The name of the S3 bucket.
            prefix (str, optional): The prefix used to filter the objects in the bucket.
                                    Default is an empty string. Must be find with '/'

        Returns:
            dict: A dictionary with two lists:
                  - 'folders': Names of folders found under the prefix (without the prefix or trailing slash).
                  - 'files': Names of the files found under the prefix (without the prefix).
                  
        Raises:
            Exception: If the bucket does not exist or if there is an error listing the objects.
        """
        pass
    
    # ------------------------- File functions ---------------------------
    
    @abstractmethod
    def read_file(self, bucket_name: str, s3_path: str, format: str | None = None) -> str:
        """
        Reads the contents of a file stored in an AWS S3 bucket without downloading it.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_path (str): The path to the file in the bucket.
            format (str, optional): The format of the file. Default is None.

        Returns:
            str: The contents of the file as a string without encoding or decoding if format is provided.

        Raises:
            Exception: If the bucket or file does not exist.
        """
        pass
    
    @abstractmethod
    def rename_file(self, bucket_name: str, old_s3_path: str, new_s3_path: str) -> None:
        """
        Renames a file in an AWS S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            old_s3_path (str): The current path of the file in the bucket.
            new_s3_path (str): The new path of the file in the bucket.

        Raises:
            Exception: If the bucket or file does not exist, or if the new path already exists.
        """
        pass
    
    @abstractmethod
    def download_file(self, bucket_name: str, s3_path: str, local_path: str) -> None:
        """
        Download a file from an AWS S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_path (str): The path to the file in the bucket.
            local_path (str): The path where the downloaded file will be saved.
            
        Raises:
            Exception: If the bucket or file does not exist.
        """
        pass
    
    @abstractmethod
    def get_presigned_url_file(self, bucket_name: str, s3_path: str) -> str:
        """
        Get a presigned URL for a file in an AWS S3 bucket. This URL can be used to download the file without authentication.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_path (str): The path to the file in the bucket.
            
        Raises:
            Exception: If the bucket or file does not exist.
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def delete_file(self, bucket_name: str, s3_path: str) -> None:
        """
        Deletes a file from an AWS S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_path (str): The path to the file in the bucket.

        Raises:
            Exception: If the bucket or file does not exist.
        """
        pass
    
     # ------------------------- Folder functions ---------------------------
    
    @abstractmethod
    def download_folder(self, bucket_name: str, s3_path: str, local_path: str) -> None:
        """
        Download a folder from an AWS S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_path (str): The path to the folder in the bucket. Must be find with '/'
            local_path (str): The path where the downloaded folder will be saved.
            
        Raises:
            Exception: If the bucket or folder does not exist.
        """
        pass

    @abstractmethod
    def upload_folder(self, bucket_name, s3_path, local_path):
        """
        Uploads a folder to an S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_path (str): The path to the folder in the bucket. Must be find with '/'
            local_path (str): The path where the uploaded folder is saved.

        Raises:
            Exception: If the bucket or folder does not exist.
        """
        pass
    
    @abstractmethod
    def delete_folder(self, bucket_name, s3_path):
        """
        Deletes a folder and all its contents from an S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_path (str): The path to the folder in the bucket. Must be find with '/'

        Raises:
            Exception: If the bucket or folder does not exist.
        """
        pass

    @abstractmethod
    def rename_folder(self, bucket_name, old_s3_path, new_s3_path):
        """
        Renames a folder in an S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            old_s3_path (str): The current path of the folder in the bucket. Must be find with '/'
            new_s3_path (str): The new path of the folder in the bucket. Must be find with '/'

        Raises:
            Exception: If the bucket or folder does not exist, or if the new path already exists.
        """
        pass
    
    # ------------------------- Buckets functions ---------------------------
    
    @abstractmethod
    def create_bucket(self, bucket_name):
        """
        Creates an S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.

        Raises:
            Exception: If the bucket already exists or if there is an error during creation.
        """
        pass

    @abstractmethod
    def delete_bucket(self, bucket_name):
        """
        Deletes an S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.

        Raises:
            Exception: If the bucket does not exist or is not empty.
        """
        pass

    @abstractmethod
    def rename_bucket(self, old_bucket_name, new_bucket_name):
        """
        Renames an S3 bucket.

        Args:
            old_bucket_name (str): The name of the existing S3 bucket.
            new_bucket_name (str): The new name for the S3 bucket.

        Raises:
            Exception: If the old bucket does not exist, if the new bucket already exists,
                    or if there is an error during the process.
        """
        pass