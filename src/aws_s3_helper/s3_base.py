from botocore.exceptions import ClientError

class S3Base:
    """
    Common methods for the S3 class.
    """
    def __init__(self, client) -> None:
        self.__client = client
    
    
    def _bucket_exists(self, bucket_name: str) -> bool:
        """
        Checks if an S3 bucket exists.

        Args:
            bucket_name (str): The name of the S3 bucket.

        Returns:
            bool: True if the bucket exists, False if it does not.

        Raises:
            Exception: If an error occurs when trying to verify the existence of the bucket.
        """
        try:
            self.__client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            error_code = int(e.response["Error"]["Code"])
            if error_code == 404:
                return False
            else:
                raise Exception(f"Error verifying the existence of the bucket: {e}")


    def _s3_path_exists(self, bucket_name: str, s3_path: str) -> bool:
        """
        Checks if a file or folder exists in the S3 bucket under the specified path.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_path (str): The path to the file or folder in the bucket.

        Returns:
            bool: True if the file or folder exists, False if it does not exist.

        Raises:
            Exception: If an error occurs when trying to verify the existence of the file or folder.
        """
        if  s3_path.endswith("/"):  # Folder
            result = self.__client.list_objects_v2(
                Bucket=bucket_name, Prefix=s3_path, Delimiter="/"
            )
            return "CommonPrefixes" in result or "Contents" in result
        else:  # File
            try:
                self.__client.head_object(Bucket=bucket_name, Key=s3_path)
                return True
            except ClientError as e:
                error_code = int(e.response["Error"]["Code"])
                if error_code == 404:
                    return False
                else:
                    raise Exception(
                        f"Error verifying the existence of the file or folder: {e}"
                    )