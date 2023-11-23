from abc import ABC, abstractmethod

class Account(ABC):
    
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_postions(self):
        yield

    @abstractmethod
    def get_futures(self):
        yield
    
    @abstractmethod
    def write_data_to_json(self):
        yield

    @abstractmethod
    def read_data_from_json(self):
        yield