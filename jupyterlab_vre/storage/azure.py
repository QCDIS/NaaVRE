from azure.storage.blob import BlobServiceClient
import uuid

class AzureStorage:

    connection_string = "DefaultEndpointsProtocol=https;AccountName=lwdatasetstorage;AccountKey=;EndpointSuffix=core.windows.net"


    @classmethod
    def test_upload(cls, file_path: str, container_name: str):

        blob_service_client = BlobServiceClient.from_connection_string(cls.connection_string)
        container = blob_service_client.get_container_client(container_name)

        if (not container.exists()):
            container.create_container()

        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_path)

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data)
        