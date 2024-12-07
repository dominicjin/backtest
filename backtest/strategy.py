import backtrader as bt
import pandas as pd
import backtrader as bt


# 定义策略
class MaCross(bt.SignalStrategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 添加MA12和MA26指标
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.ma12 = bt.indicators.MovingAverageSimple(self.data.close, period=12)
        self.ma26 = bt.indicators.MovingAverageSimple(self.data.close, period=26)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
 
        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
 
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            
            cash = self.broker.get_cash()
            total_value = self.broker.get_value()
            print(f"Cash: {cash}  Portfolio Value: {total_value}")
            self.bar_executed = len(self)
 
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
 
        self.order = None
    
    
    def next(self):

        cash = self.broker.get_cash()
        amount_to_invest = 200000
        size = amount_to_invest / self.data.close[0]
        
        # 如果MA12 > MA26，买入
        if self.ma12[0] > self.ma26[0]:
            if cash < amount_to_invest:
                return 
            self.order = self.buy(size=size) # 如果没有持仓，执行买入
                
        # 如果MA12 < MA26，卖出
        elif self.ma12[0] < self.ma26[0]:
            if self.position:  # 如果有持仓，执行卖出
                self.order = self.sell(size=self.position.size)

def back_test(start_date, end_date, principal=1000000.0, commission=0.0, slip=0.001):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MaCross)
    cerebro.broker.set_cash(principal)
    cerebro.broker.setcommission(commission)
    cerebro.broker.set_slippage_perc(slip)

    df = pd.read_csv("./data/data.csv", index_col='date')

    #转化index类型
    df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
    start_date = pd.to_datetime(str(start_date))
    end_date = pd.to_datetime(str(end_date))
    data = bt.feeds.PandasData(dataname=df, fromdate=start_date, todate=end_date)  # 加载数据
    cerebro.adddata(data)  # 将数据传入回测系统

    print('Starting Portfolio Value: %.4f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.4f' % cerebro.broker.getvalue())

    rate = (cerebro.broker.getvalue() - principal) / principal * 100
    # cerebro.plot()
    # print("result: ",rate, cerebro.broker.getvalue())

    return rate, cerebro.broker.getvalue()
    



if __name__ == "__main__":
    print(back_test('20180601', '20180731'))