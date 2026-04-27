import os
import sys
import json
import pandas as pd
from pandas import DataFrame

from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection

from visa_approval_prediction_app.entity.config_entity import DataValidationConfig
from visa_approval_prediction_app.entity.artifact_entity import DataValidationArtifact, DataIngestionArtifact
from visa_approval_prediction_app.exception import VisaAppException
from visa_approval_prediction_app.logger import logging
from visa_approval_prediction_app.utils.main_utils import read_yaml_file, write_yaml_file
from visa_approval_prediction_app.constants import SCHEMA_FILE_PATH


class DataValidation:
    def __init__(self,data_validation_config:DataValidationConfig,data_ingestion_artifact:DataIngestionArtifact):
        """
        :param data_validation_config: configuration for data validation
        """
        try:
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self._schema_config =read_yaml_file(file_path=SCHEMA_FILE_PATH)
        except Exception as e:
            raise VisaAppException(e,sys)
    
    def validate_number_of_columns(self,dataframe:DataFrame)->bool:
        """
        Method Name :   validate_number_of_columns
        Description :   This method validates the number of columns
        
        Output      :   Returns bool value based on validation results
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            status = len(dataframe.columns) == len(self._schema_config["columns"])
            logging.info(f"Is required column present: [{status}]")
            return status
        except Exception as e:
            raise VisaAppException(e,sys)
    
    @staticmethod
    def read_data(file_path:str)->DataFrame:
        try:
            dataframe = DataFrame()
            if os.path.exists(file_path):
                dataframe = DataFrame(pd.read_csv(file_path))
                logging.info(f"Data read successfully from file path: {file_path}")
            else:
                logging.info(f"File path: {file_path} does not exist")
            return dataframe
        except Exception as e:
            raise VisaAppException(e,sys)
        
    def is_column_exist(self,dataframe:DataFrame)->bool:
        """
        Method Name :   is_column_exist
        Description :   This method validates the existence of a numerical and categorical columns
        
        Output      :   Returns bool value based on validation results
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            dataframe_columns = dataframe.columns
            missing_numerical_columns = []
            missing_categorical_columns = []
            for column in self._schema_config["numerical_columns"]:
                if column not in dataframe_columns:
                    missing_numerical_columns.append(column)

            if len(missing_numerical_columns)>0:
                logging.info(f"Missing numerical column: {missing_numerical_columns}")


            for column in self._schema_config["categorical_columns"]:
                if column not in dataframe_columns:
                    missing_categorical_columns.append(column)

            if len(missing_categorical_columns)>0:
                logging.info(f"Missing categorical column: {missing_categorical_columns}")

            return False if len(missing_categorical_columns)>0 or len(missing_numerical_columns)>0 else True
        except Exception as e:
            raise VisaAppException(e,sys)
    
    def detect_dataset_drift(self,reference_df:DataFrame, current_df:DataFrame)->bool:
        """
        Method Name :   detect_dataset_drift
        Description :   This method validates if drift is detected
        
        Output      :   Returns bool value based on validation results
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            data_drift_profile = Profile(sections=[DataDriftProfileSection()])

            data_drift_profile.calculate(reference_df, current_df)

            report = data_drift_profile.json()
            json_report = json.loads(report)

            write_yaml_file(file_path=self.data_validation_config.drift_report_file_path, content=json_report)

            n_features = json_report["data_drift"]["data"]["metrics"]["n_features"]
            n_drifted_features = json_report["data_drift"]["data"]["metrics"]["n_drifted_features"]

            logging.info(f"{n_drifted_features}/{n_features} drift detected.")
            drift_status = json_report["data_drift"]["data"]["metrics"]["dataset_drift"]
            return drift_status
        except Exception as e:
            raise VisaAppException(e, sys) from e

    
    def initiate_data_validation(self) -> DataValidationArtifact:
        """
        Method Name :   initiate_data_validation
        Description :   This method initiates the data validation component for the pipeline
        
        Output      :   Returns bool value based on validation results
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            validation_error_msg = ""
            logging.info("Starting data validation")
            train_df, test_df = (DataValidation.read_data(file_path =self.data_ingestion_artifact.trained_file_path), DataValidation.read_data(file_path = self.data_ingestion_artifact.test_file_path))
            
            status = self.validate_number_of_columns(dataframe=train_df)
            logging.info(f"All required columns present in training dataframe: {status}")
            if not status:
                validation_error_msg += f"Columns are missing in training dataframe."
            status = self.validate_number_of_columns(dataframe=test_df)

            logging.info(f"All required columns present in testing dataframe: {status}")
            if not status:
                validation_error_msg += f"Columns are missing in test dataframe."

            status = self.is_column_exist(dataframe=train_df)

            if not status:
                validation_error_msg += f"Columns are missing in training dataframe."
            status = self.is_column_exist(dataframe=test_df)

            if not status:
                validation_error_msg += f"columns are missing in test dataframe."

            validation_status = len(validation_error_msg) == 0

            if validation_status:
                drift_status = self.detect_dataset_drift(train_df, test_df)
                if drift_status:
                    logging.info(f"Drift detected.")
                    validation_error_msg = "Drift detected"
                else:
                    validation_error_msg = "Drift not detected"
            else:
                logging.info(f"Validation_error: {validation_error_msg}")

            data_validation_artifact = DataValidationArtifact(
            validation_status=validation_status, 
            message=validation_error_msg, 
            drift_report_file_path=self.data_validation_config.drift_report_file_path)
            
            logging.info(f"Data validation artifact: {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e:
            raise VisaAppException(e, sys) from e