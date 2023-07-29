
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
    def __init__(self,initial_funds,loss_rate,AUM) -> None:
        self.initial_funds = initial_funds
        self.loss_rate = loss_rate
        self.AUM = AUM

    def get_current_loss_ratio(self,dex,stop_loss_points):
        # loss level
        first_level = self.initial_funds * self.loss_rate
        second_level = first_level / 2
        third_level = second_level / 2

        # leverage mark
        high = self.initial_funds
        medium = high - first_level
        low = medium - second_level

        position_size = 0
        if dex >= high:
            position_size = first_level/ stop_loss_points
        elif medium <= dex < high:
            position_size = second_level/ stop_loss_points
        elif dex <= medium:
            position_size = third_level/ stop_loss_points
        return round(position_size,3)



# rsm = Risk_manager(1600,0.02,0.2)

# for dex in range(1300,1700,10):

#     pos = rsm.get_current_loss_ratio(dex,88)
#     print(dex,pos)

