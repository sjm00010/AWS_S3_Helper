from botocore.exceptions import ClientError


def bucket_exists(client, bucket_name: str) -> bool:
    """
    Verifica si un bucket de S3 existe.

    Args:
        bucket_name (str): El nombre del bucket de S3.

    Returns:
        bool: True si el bucket existe, False si no existe.

    Raises:
        Exception: Si ocurre un error al intentar verificar la existencia del bucket.
    """
    try:
        client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        error_code = int(e.response["Error"]["Code"])
        if error_code == 404:
            return False
        else:
            raise Exception(f"Error al verificar la existencia del bucket: {e}")


def s3_path_exists(client, bucket_name: str, s3_path: str) -> bool:
    """
    Verifica si un archivo o carpeta existe en el bucket de S3 bajo la ruta especificada.

    Args:
        bucket_name (str): El nombre del bucket de S3.
        s3_path (str): La ruta del archivo o carpeta en el bucket.

    Returns:
        bool: True si el archivo o carpeta existe, False si no existe.

    Raises:
        Exception: Si ocurre un error al intentar verificar la existencia del archivo o carpeta.
    """
    if s3_path.endswith("/"):  # Es un directorio
        result = client.list_objects_v2(
            Bucket=bucket_name, Prefix=s3_path, Delimiter="/"
        )
        return "CommonPrefixes" in result or "Contents" in result
    else:  # Es un archivo
        try:
            client.head_object(Bucket=bucket_name, Key=s3_path)
            return True
        except ClientError as e:
            error_code = int(e.response["Error"]["Code"])
            if error_code == 404:
                return False
            else:
                raise Exception(
                    f"Error al verificar la existencia del archivo o carpeta: {e}"
                )
