from pathlib import Path
import joblib
import urllib
import json

from src.logger import setup_logger
from src.security.utils import url_decode
from src.classifire.request import BaseRequest

logger = setup_logger()


class ThreatClassifire:
    def __init__(self):
        self.main_path = Path(__file__).parent / 'models'
        self.classifier_model_path = self.main_path / 'predictor.joblib'

        try:
            self.classifier_model = joblib.load(self.classifier_model_path)
        except FileNotFoundError:
            logger.info(f"Model not found at {self.classifier_model_path}. Please check the path.")
            self.classifier_model = None

    def __remove_new_line(self, text: str) -> str:
        text = text.strip()
        return ' '.join(text.splitlines())

    def __remove_multiple_whitespaces(self, text: str) -> str:
        return ' '.join(text.split())

    def __clean_pattern(self, pattern: str) -> str:
        pattern = urllib.parse.unquote(pattern)
        pattern = self.__remove_new_line(pattern)
        pattern = pattern.lower()
        pattern = self.__remove_multiple_whitespaces(pattern)
        return pattern

    def __is_valid(self, parameter: str | None) -> bool:
        return parameter is not None and parameter != ''

    def __extract_parameters(self, req: BaseRequest) -> tuple[list[str], list[str]]:
        """Извлекает параметры и их местоположения из запроса."""
        parameters = []
        locations = []

        if self.__is_valid(req.request):
            parameters.append(self.__clean_pattern(req.request))
            locations.append('Request')
        if self.__is_valid(req.body):
            parameters.append(self.__clean_pattern(req.body))
            locations.append('Body')

        headers_to_check = {
            'Cookie': 'Cookie',
            'User_Agent': 'User Agent',
            'Accept_Encoding': 'Accept Encoding',
            'Accept_Language': 'Accept Language',
            'Referer': 'Referer',
            'Cache_Control': 'Cache Control',
        }

        for header, location in headers_to_check.items():
            if header in req.headers and self.__is_valid(req.headers[header]):
                parameters.append(self.__clean_pattern(req.headers[header]))
                locations.append(location)

        return parameters, locations

    def __parse_parameters(self, req: BaseRequest) -> tuple[dict, dict]:
        """Парсит параметры из запроса и тела."""
        request_parameters = {}
        body_parameters = {}

        if self.__is_valid(req.request):
            request_parameters = urllib.parse.parse_qs(self.__clean_pattern(req.request))

        if self.__is_valid(req.body):
            body_parameters = urllib.parse.parse_qs(self.__clean_pattern(req.body))
            if not body_parameters:
                try:
                    body_parameters = json.loads(self.__clean_pattern(req.body))
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON body: {e}")

        return request_parameters, body_parameters

    def classify_request(self, req: BaseRequest) -> BaseRequest:
        """
        Классифицирует угрозы в запросе.
        """
        if not isinstance(req, BaseRequest):
            raise TypeError("Object should be a BaseRequest!")

        if self.classifier_model is None:
            logger.error("Classifier model is not loaded. Cannot classify requests.")
            req.threats = {'error': 'Model not loaded'}
            return req

        # Извлечение параметров и их местоположений
        parameters, locations = self.__extract_parameters(req)

        # Классификация угроз
        req.threats = {}
        if parameters:
            predictions = self.classifier_model.predict(parameters)
            for idx, pred in enumerate(predictions):
                if pred != 'valid':
                    req.threats[pred] = locations[idx]

        # Проверка на подмену параметров
        request_parameters, body_parameters = self.__parse_parameters(req)

        for name, value in request_parameters.items():
            for e in value:
                parameters.append([len(e)])
                locations.append('Request')

        for name, value in body_parameters.items():
            if isinstance(value, list):
                for e in value:
                    parameters.append([len(e)])
                    locations.append('Body')
            else:
                parameters.append([len(value)])
                locations.append('Body')

        if not req.threats:
            req.threats['valid'] = ''

        return req