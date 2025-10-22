from supermemory import Supermemory
from typing import Dict, List, Any
from datetime import datetime
from dotenv import dotenv_values

config = dotenv_values(".env")

class DocumentProcessor:
    def __init__(self):
        self.client = Supermemory(
            api_key=config["SUPERMEMORY_API_KEY"],
        )

    def upload_files(self, file_path: str, container: List[str]) -> Dict:
        try:
            with open(file_path, 'rb') as file:
                result = self.client.memories.upload_file(
                    file=file,
                    container_tags=container #type: ignore
                )
                print(result)
            result_dic = result.to_dict()
            return result_dic
        except Exception as e:
            print(f"File upload error: {e}")
            raise

    def upload_url(self, url: str, collection: str, metadata: Dict[str, Any] = None) -> Dict:
        """Upload URL content to Supermemory"""
        if metadata is None:
            metadata = {}

        try:
            result = self.client.memories.add(
                content=url,
                container_tag=collection,
                metadata={
                    'type': 'url',
                    'originalUrl': url,
                    'uploadedAt': datetime.now().isoformat(),
                    **metadata
                }
            )
            return result
        except Exception as e:
            print(f"URL upload error: {e}")
            raise

    def get_document_status(self, document_id: str) -> Dict:
        """Check document processing status"""
        try:
            memory = self.client.memories.get(document_id)
            return {
                'id': memory.id,
                'status': memory.status,
                'title': memory.title,
                'progress': memory.metadata.get('progress', 0) if memory.metadata else 0
            }
        except Exception as e:
            print(f"Status check error: {e}")
            raise

    def list_documents(self, collection: str) -> List[Dict]:
        """List all documents in a collection"""
        try:
            memories = self.client.memories.list(
                container_tags=[collection],
                limit=50,
                sort='updatedAt',
                order='desc'
            )

            return [
                {
                    'id': memory.id,
                    'title': (memory.title or
                            memory.metadata.get('originalName') or
                            'Untitled' if memory.metadata else 'Untitled'),
                    'type': (memory.metadata.get('fileType') or
                           memory.metadata.get('type') or
                           'unknown' if memory.metadata else 'unknown'),
                    'uploadedAt': memory.metadata.get('uploadedAt') if memory.metadata else None,
                    'status': memory.status,
                    'url': memory.metadata.get('originalUrl') if memory.metadata else None
                }
                for memory in memories.memories
            ]
        except Exception as e:
            print(f"List documents error: {e}")
            raise
