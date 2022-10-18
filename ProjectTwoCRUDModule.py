from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps


class AnimalShelter(object):
    """
    CRUD operations for Animal collection in MongoDB
    """
    def __init__(self, username, password):
        # Initializing the MongoClient
        # Access the MongoDB databases and collections.
        self.client = MongoClient('mongodb://%s:%s@localhost' % (username, password))
        self.database = self.client['AAC']['animals']
        # print("AnimalShelter instantiated!")

    def read(self, search_criteria: dict):
        """
        Query for documents.
        :param search_criteria: dictionary containing field/s and value/s for search criteria
        :return: results as cursor object
        """
        results = self.database.find(search_criteria, {"addresses": {"$slice": [0, 1]}, '_id': False})
        return results

    def create(self, document: dict):
        """
        Insert a document.
        :param: document: Document to insert.
        :return: True if successful, Exception if unsuccessful
        """
        if document:
            if isinstance(document, dict):  # Parameter is restricted to dict type, but this can provide extra clarification.
                self.database.insert_one(document)
                return True
        return False

    def remove(self, remove_criteria: dict):
        """
        Deletes a single document from a specified Mongo database.
        :param remove_criteria: dictionary containing field/s and value/s for removal
        :return: dictionary with number of documents deleted
        """
        if remove_criteria:
            delete_result = self.database.delete_many(remove_criteria)
            return {"Deleted": delete_result.deleted_count}
        print("[WARNING] remove criteria empty. Delete aborted to prevent data loss.")
        return remove_criteria

    def update(self, update_criteria: dict, updated_document: dict):
        """
        Update document/s that match update criteria to fields and values within updated document.
        :param update_criteria: dictionary containing field/s and value/s to match for update.
        :param updated_document: dictionary containing field/s and value/s to update or append.
        :return: dictionary with number of matches and number of updated documents
        """
        if update_criteria:
            update_results = self.database.update_many(update_criteria, {"$set": updated_document})
            return dumps(update_results, indent=2)
        print("[WARNING] Update criteria empty. Update aborted to maintain data integrity.")
        return update_criteria




#testing = AnimalShelter("aacuser", "password")
#print(dumps(testing.read({"animal_id": "A725717"}), indent=2))
