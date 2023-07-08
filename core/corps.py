## soldier                 ## 血量               ## 步程        ## 活动范围             ##盈亏                  ## 动态止损                         ## 下单位置
## 巡逻兵——Patrolman：      0.1/0.2/0.2/0.1         1               内                  用盈利来决定亏损        盈利delta/2开始 / 平移止损位

# 近战兵——melee ：          0.1/0.2/0.2/0.1         1               外                  用亏损来决定盈利        盈利delta/2开始 / 平移止损位       
# 远征兵——Expeditionary：   0.1/0.2/0.2/0.1         2               外                  用亏损来决定盈利        盈利delta/2开始 / 平移止损位
# 敢死队——Expendables：     0.05/0.1/0.1/0.05     爆破末位            外                  用亏损来决定盈利        盈利delta/2开始 / 平移止损位

# 游击兵——Guerrilla         0.05/0.1/0.1/0.05       1              内/外                0.001                   0.008开始      / 回撤0.002 止损
# 影兵——Shadow              0.05/0.1/0.1/0.05     爆破首位          内/外                用盈利来决定亏损          盈利delta/2开始 / 回撤0.002止损     反转价-观察价之间下单，观察价吃单到爆破首位，止损反转位
# 中军大帐——citadel



## Military system 
#   军工系统
#   头衔        平南/北将军      镇南/北将军     征南/北将军     大将军
#   战功值      50              100             200         500
#   手数        x2              x3              x4          x5


class Corps:
    def __init__(self) -> None:
        pass
    
    def queque_melee(self,sds,base_qty):
        queque = []
        i = 0
        for sd in sds:
            sd.to_melee(base_qty)
            if sd.side == 'open_long':
                sd.id = 'long_melee_'+ str(i)
            elif sd.side == 'open_short':
                sd.id = 'short_melee_'+ str(i)
            queque.append(sd)
            i+=1
        return queque

    def queque_expedition(self,sds,base_qty):
        queque = []
        i = 0
        for sd in sds:
            sd.to_expedition(base_qty)
            if sd.side == 'open_long':
                sd.id = 'long_expedition_'+ str(i)
            elif sd.side == 'open_short':
                sd.id = 'short_expedition_'+ str(i)
            queque.append(sd)
            i+=1
        return queque

class Soldier:
    def __init__(self,side,entry,sl,qty) -> None:
        self.side = side
        self.entry = entry
        self.tp = 0
        self.sl = sl
        self.qty = qty 
        self.id = ''
        self.reborn = False

    def to_melee(self,base_qty):
        pace = 0.8
        delta = abs(self.entry - self.sl)
        if self.side == 'open_long':
            if self.qty == base_qty:
                self.tp = self.entry + delta
            elif self.qty == base_qty * 2:
                self.tp = self.entry + round(delta * pace)

        elif self.side == 'open_short':
            if self.qty == base_qty:
                self.tp = self.entry - delta
            elif self.qty == base_qty * 2:
                self.tp = self.entry - round(delta * pace)

    def to_expedition(self,base_qty):
        long_pace = 2
        short_pace = 1.5
        delta = abs(self.entry - self.sl)
        if self.side == 'open_long':
            if self.qty == base_qty:
                self.tp = self.entry + round(delta * long_pace)
            elif self.qty == base_qty * 2:
                self.tp = self.entry + round(delta * short_pace)
        elif self.side == 'open_short':
            if self.qty == base_qty:
                self.tp = self.entry - round(delta * long_pace)
            elif self.qty == base_qty * 2:
                self.tp = self.entry - round(delta * short_pace)

    def to_expendable(self,base_qty,long_target,short_target):
        base_qty = base_qty /2
        print(f"expendable's base qty is {base_qty}")
        short_pace = 2.5
        delta = abs(self.entry - self.sl)
        if self.side == 'open_long':
            if self.qty == base_qty:
                self.tp = long_target
            elif self.qty == base_qty * 2:
                self.tp = self.entry + delta * short_pace
        elif self.side == 'open_short':
            if self.qty == base_qty:
                self.tp = short_target
            elif self.qty == base_qty * 2:
                self.tp = self.entry - delta * short_pace
 

