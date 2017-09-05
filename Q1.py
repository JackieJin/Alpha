import datetime
import queue
from core.portfolio_handler import PortfolioHandler
from constant_position_sizer import ConstantPositionSizer
from strategy.constant_mix_strategy import ConstantMixStrategy
from core.price_handler import PriceHandler
from data.data_factory import StockData
from core.excution_handler import SimulationExecutionHandler

def run_q1():

    initial_equity  = 1000000.0
    start_date      = datetime.datetime(1999, 1, 1)
    end_date        = datetime.datetime.today()

    strategy        = ConstantMixStrategy({'AAPL': 0.4, 'C': 0.6})
    events_queue    = queue.Queue()
    position_sizer  = ConstantPositionSizer()
    s1              = StockData('quandl', ['AAPL', 'C'])
    data_symbols    = [s1]
    init_tickers    = ['AAPL', 'C']
    ph              = PriceHandler(data_symbols, init_tickers, start_date, end_date)
    execution_handler   = SimulationExecutionHandler()
    port_handler    = PortfolioHandler(initial_equity,
                     events_queue,
                     price_handler=ph,
                     position_sizer=position_sizer,
                     risk_manager=None,
                     execution_handler = execution_handler,
                     strategy= strategy,
                     statistics= None,
                     start_time = datetime.datetime(1999, 1, 4)

                     )
    port_handler.initialize_parameters()
    port_handler.run_session()
    print('finished')

if __name__ == "__main__":
    run_q1()