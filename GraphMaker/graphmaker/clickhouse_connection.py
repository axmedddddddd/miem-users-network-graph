from typing import TypeVar
import sqlalchemy as sa
from sqlalchemy import NullPool
import pandas as pd

SelfClickHouseConnection = TypeVar("SelfClickHouseConnection", bound="ClickHouseConnection")

class ClickHouseConnection:
    """Класс контекстного менеджера для работы с ClickHouse"""
    
    def __init__(self, host: str, username: str, password: str, port: str = "9000"):
        """
        Параметры:
            host: хост ClickHouse
            username: имя пользователя ClickHouse
            password: пароль пользователя ClickHouse
            port: порт ClickHouse
        """
        
        self.session = None
        self.__host = host
        self.__port = port
        self.__username = username
        self.__password = password
        
    def __get_url(self) -> str:
        """Метод формирует connection string для подключения к ClickHouse"""
        
        url = "clickhouse+native://{username}:{password}@{host}:{port}"
        url = url.format(
            host = self.__host,
            port = self.__port,
            username = self.__username,
            password = self.__password
        )
        return url
        
    def __enter__(self: SelfClickHouseConnection) -> SelfClickHouseConnection:
        engine = sa.create_engine(self.__get_url(), poolclass=NullPool)
        self.session = engine.connect()
        return self
    
    def __exit__(self, exception_type, exception_value, traceback):
        self.session.close()
        
    def read_sql(self, query: str) -> pd.DataFrame:
        """
        Запрос к БД через фреймворк pandas
        
        Параметры:
            query: SQL в формате строки
            
        Возвращает:
            датафрейм с результатами запроса
        """
        
        with self as connector:
            return pd.read_sql(query, con=connector.session)


if __name__ == "__main__":
    connection_manager = ClickHouseConnection(host=config.ch_host, username=config.ch_username, password=config.ch_password)
    connection_manager.read_sql("SELECT * FROM system.tables")
