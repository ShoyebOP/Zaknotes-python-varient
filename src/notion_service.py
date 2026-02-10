import logging
from notion_client import Client

logger = logging.getLogger(__name__)

class NotionService:
    def __init__(self, notion_secret: str, database_id: str):
        self.client = Client(auth=notion_secret)
        self.database_id = database_id

    def check_connection(self) -> bool:
        """
        Verifies the connection to Notion by retrieving the database metadata.
        """
        try:
            self.client.databases.retrieve(database_id=self.database_id)
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Notion: {e}")
            return False
