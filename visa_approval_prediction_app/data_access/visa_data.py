from visa_approval_prediction_app.configuration.mongo_db_connection import MongoDBClient
from visa_approval_prediction_app.constants import DATABASE_NAME
from visa_approval_prediction_app.exception import VisaAppException
import pandas as pd
import sys
from typing import Optional
import numpy as np



class visaData:
    """
    This class help to export entire mongo db record as pandas dataframe
    """

    def __init__(self):
        """
        """
        try:
            self.mongo_client = MongoDBClient(database_name=DATABASE_NAME)
        except Exception as e:
            raise VisaAppException(e,sys)
        

    def export_collection_as_dataframe(self,collection_name:str,database_name:Optional[str]=None)->pd.DataFrame:
        try:
            """
            export entire collection as dataframe:
            return pd.DataFrame of collection
            """
            if database_name is None:
                collection = self.mongo_client.database[collection_name]
            else:
                collection = self.mongo_client[database_name][collection_name]

            print(f"DEBUG: Attempting to fetch from collection '{collection}'")
            data = list(collection.find())
            print(f"DEBUG: Found {len(data)} records")
            
            df = pd.DataFrame(data)
            print(f"DEBUG: DataFrame shape: {df.shape}")
            
            if "_id" in df.columns.to_list():
                df = df.drop(columns=["_id"], axis=1)
            df.replace({"na":np.nan},inplace=True)
            return df
        except Exception as e:
            raise VisaAppException(e,sys)