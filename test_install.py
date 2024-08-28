from dotenv import dotenv_values
from aws_s3_helper.s3 import S3

# Crea una instancia de la clase S3
env = dotenv_values()
s3 = S3(
    aws_access_key_id=env["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=env["AWS_SECRET_ACCESS_KEY"],
    aws_region=env["AWS_REGION"],
)

s3.delete_folder("pruebas-files-novo", "test_folder/")