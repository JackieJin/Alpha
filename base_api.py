from abc import ABC,abstractclassmethod

class AbstractData(ABC):

    @abstractclassmethod
    def get_data(self, ticker, start_date, end_date):
        pass


    def _rename_columns(self, data):
        return