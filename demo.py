from visa_approval_prediction_app.logger import get_logger, demo_logger
from visa_approval_prediction_app.exception import VisaAppException
import sys

demo_logger("welcome to visa approval prediction app")

try:
    a = 1 / 0
except Exception as e:
    raise VisaAppException(e, sys)