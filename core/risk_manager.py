
## risk
## shanon 

## high water mark
###      RR = 2
###      AUM_loss_rate = 20%
###      initial_loss_rate = 2%   : 
#           if loss, 
#               AUM_loss_rate = 18% , 
#               second_loss_rate = initial_loss_rate /2 = 1%,
#           then loss,
#                AUM_loss_rate = 17%
#               last_loss_rate = second_loss_rate /2  =  0.5%
#           then win,
#                AUM_loss_rate = 17.5%
#               last_loss_rate =  0.5%
#           then win,
#                AUM_loss_rate = 18%
#               second_loss_rate = last_loss_rate * 2 = 1%
#           then win,
#                AUM_loss_rate = 19%
#               second_loss_rate = 1%
#           then win,
#                AUM_loss_rate = 19%
#               initial_loss_rate = second_loss_rate * 2 = 2%
###      

## break & butter setup
###     london     14:00 - 17:00
###     NY         21:30 - 11:00


class Risk_manager():
    def __init__(self,initial_funds,loss_rate,AUM,balance_rate) -> None:
        self.initial_funds = initial_funds
        self.loss_rate = loss_rate
        self.AUM = AUM
        self.balance_rate = balance_rate

    def get_current_loss_ratio(self,dex,stop_loss_points):
        # loss level
        first_level = self.initial_funds * self.loss_rate
        second_level = first_level / 2
        third_level = second_level / 2

        # leverage mark
        high = self.initial_funds
        medium = high - first_level

        position_size = 0
        if dex >= high:
            position_size = dex * self.loss_rate/ stop_loss_points
        elif medium <= dex < high:
            position_size = second_level/ stop_loss_points
        elif dex <= medium:
            position_size = third_level/ stop_loss_points
        return round(position_size,3)
    
    def rebalance(self,future,spot):
        delta = abs(future - spot)
        if delta > 100:
            totoal = future + spot
            alt_future = totoal * self.balance_rate
            trans_amount = round(abs(alt_future - future))

            if alt_future > future:
                return 'to_future',trans_amount
            elif alt_future < future:
                return 'to_spot',trans_amount
            else:
                return '',0
        else:
            return '',0







# rsm = Risk_manager(5000,0.01,0.2,0.5)

# future = 5000
# spot = 2000

# to_where,amount = rsm.rebalance(future,spot)

# print(to_where,amount )
# for dex in range(4800,5200,10):

#     pos = rsm.get_current_loss_ratio(dex,88)
#     print(dex,pos)

