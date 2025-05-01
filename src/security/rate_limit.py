import time


class RateClinetBaseSingle(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance


class RateClientBucket(RateClinetBaseSingle):
    def __init__(self) -> None:
        # Проверяем, была ли уже инициализация
        if not hasattr(self, "_initialized"):
            self.__client_bucket: dict[str, list[int | float]] = {}
            # Флаг, чтобы избежать повторной инициализации
            self._initialized = True

    @property
    def client_bucket(self) -> dict:
        return self.__client_bucket

    @client_bucket.setter
    def client_bucket(self, value: dict) -> None:
        if not isinstance(value, dict):
            raise ValueError("client_bucket должен быть словарем (dict).")
        self.__client_bucket = value

    def add_client(self, ip_address: str, value: int | float) -> None:
        if ip_address not in self.__client_bucket:
            self.__client_bucket[ip_address] = []
        self.__client_bucket[ip_address].append(value)

    def removed_expired_client(self, ip_address: str, ttl: int) -> None:
        current_time = int(time.time())

        if ip_address in self.__client_bucket:
            self.__client_bucket[ip_address] = list(
                filter(
                    lambda client_time: current_time - client_time < ttl,
                    self.__client_bucket[ip_address],
                )
            )
            return self.__client_bucket[ip_address]