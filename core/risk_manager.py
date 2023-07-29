
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
    def __init__(self) -> None:
        pass
