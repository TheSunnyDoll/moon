## fvg
当前k线的前一根k线H/L 与 后一根k线的 H/L 之间的差值  

## ob 
没有fvg的ob 不算有效ob，即已经被缓解的ob 失效

## IFC
被突破的ob，强效s/r

## valid pullback
bull，突破前最高k线的最低点，然后突破最高点，是vp，算一个leg  
bear，突破前最低k线的最高点，然后突破最低点，是vp，算一个leg

## liquidity
市场在上涨/下跌前需要流动性，银行和机构不在意你的结构，只在意流动性
### external liquidity
### internal liquidity
次级结构  
1.inducement   回撤1点 ，50-50 概率区  

## engineer liquidity（ENG LQD）  
在极限ob前的内部高点
回撤2点，高概率区  

## Identify valid structure
1.标记出所有的swing_h , swing_l  (major)
2.一段bull trend ,出现新的一个leg，swingH 突破前一个swingH，swingL突破前一个swingL，那么它被称为IVS,被swingH确认  
3.一段bear trend ,出现新的一个leg，swingL 突破前一个swingL，swingH突破前一个swingH，那么它被称为IVS,被swingL确认  
exp：bear，在主结构下，打破次结构的高点的低点。 bull，打破次结构的低点的高点。称为bos

## OF
1.没有被缓解的最后的反趋势动作

## OB
1.一段sharp的最后的反趋势k线

## IFC
带sweep 的OB

## BOS
实体突破

## single candle mitigation entry 
1.ob entry  
2.previous candle high sweep and close below high  --- entry previous entity high (bear)


## ping pong entry