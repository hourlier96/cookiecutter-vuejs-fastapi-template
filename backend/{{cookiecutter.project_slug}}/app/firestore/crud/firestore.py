import google.cloud.firestore as firestore
from app.core.config import settings
from app.core.cloud_logging import Singleton


class Firestore(metaclass=Singleton):
    def __init__(self) -> None:
        # Searches first from .env, or infer if not specified
        if settings.GCLOUD_PROJECT_ID:
            self.client = firestore.Client(project=settings.GCLOUD_PROJECT_ID)
        else:
            self.client = firestore.Client()

    def get_all_documents(self, collection_name: str, as_dict=True) -> list[dict]:
        doc_list = self.client.collection(collection_name).get()
        if not as_dict:
            return doc_list

        dict_list = []
        for document in doc_list:
            dict_list.append(Firestore._get_doc_as_dict(document))
        return dict_list

    def get_document(
        self, collection_name: str, document_id: str, as_dict=True
    ) -> firestore.DocumentReference | dict:
        doc = self.client.collection(collection_name).document(document_id).get()
        if not as_dict:
            return doc

        return Firestore._get_doc_as_dict(doc)

    def add_document(self, collection_name: str, data: dict) -> firestore.DocumentReference:
        return self.client.collection(collection_name).add(data)

    def update_document(
        self, collection_name: str, document_id: str, data: dict
    ) -> firestore.DocumentReference:
        return self.client.collection(collection_name).document(document_id).update(data)

    def delete_document(self, collection_name: str, document_id: str):
        return self.client.collection(collection_name).document(document_id).delete()

    @staticmethod
    def _get_doc_as_dict(doc: firestore.DocumentSnapshot) -> dict:
        if not doc.exists:
            return None
        element = doc.to_dict()
        element["id"] = doc.id
        return element
