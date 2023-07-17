# candle analyze

## move[lowest,highest]
## bear--- lowest set , highest then set(single candle),then highest push up by other candle 

class Move():
    def __init__(self) -> None:
        self.lowest = 0
        self.highest = 0
        self.bias = ''

    def new_move(self,bias):
        # if bias == 'bear':
            # if ohcl[l] < self.lowest:
            #     self.lowest = ohcl[l]
            #     self.highest = ohcl[h]

        pass

    def update(self,bias):
        # bear , 定低寻高。 bull,定高寻低。
        # if bias == 'bear':
        #     if ohcl[h] > self.highest:
        #         self.highest = ohcl[h]

        # if ohcl[l] < previous-bear[lowest] ------> new pullback move
        pass

class Candle():
    def __init__(self) -> None:
        self.current_bias = ''              # hft profile

        self.hft_supply_h = 0
        self.hft_supply_l = 0

        self.lft_supply_h = 0
        self.lft_supply_l = 0


        self.external_lqd_h = 0             # hft_h
        self.extreme_ob_h = 0
        self.extreme_ob_l = 0
        
        self.eng_lqd_bear = 0                # below the extrem ob , lft_external_lqd  
        self.idm = 0
        
        self.last_bos = 0                   # previous lowest - bear  # previous highest - bull

        self.wick_highest = 0
        self.entity_highest = 0

        self.last_potential_bb_h = 0 
        self.last_potential_bb_l = 0 

        self.last_choch = 0

        self.eng_lqd_bull = 0
        self.external_lqd_l = 0             # hft_l

        self.lft_demand_h = 0
        self.lft_demand_l = 0

        self.hft_demand_h = 0
        self.hft_demand_l = 0



    def get_history_candle():
        pass

    def get_profile():
        pass

    def get_current_candle():
        pass

    def get_current_candle_behavior():
        pass

    def get_last_ob():
        pass

    def get_last_sweep():
        pass

    def get_last_bos():
        pass

    def get_last_choch():
        pass

