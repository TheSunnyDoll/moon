from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
long_orders = []
short_orders = []

long_tp = 0
short_tp = 0
mul = 0
qty = 0
dir = ''
@app.route('/')
def home():
    return render_template('index.html', long_orders=long_orders, short_orders=short_orders,mul=mul,qty=qty, dir=dir ,long_tp=long_tp , short_tp=short_tp)

@app.route('/calculate', methods=['POST'])
def calculate():
    global long_orders
    global short_orders
    global mul
    global qty
    global dir

    global long_tp
    global short_tp
    long_start = int(request.form['long_start'])
    long_end = int(request.form['long_end'])
    short_start = int(request.form['short_start'])
    short_end = int(request.form['short_end'])
    dex = int(request.form['balance'])

    btc_fc = FireChain(long_start,long_end,short_start,short_end)
    long_tp = btc_fc.select_best_c_pct(btc_fc.long_start,btc_fc.long_end)
    short_tp = btc_fc.select_best_c_pct(btc_fc.short_start,btc_fc.short_end)

    btc_fc.get_chains()
    long_orders = btc_fc.list_orders(btc_fc.long_unit,btc_fc.long_chains,'long')
    short_orders = btc_fc.list_orders(btc_fc.short_unit,btc_fc.short_chains,'short')

    mul,qty,dir = btc_fc.select_best_multi(dex)
    long_tp = qty * long_tp
    short_tp = qty * short_tp

    return redirect(url_for('home'))

@app.route('/reset')
def reset():
    global long_orders
    global short_orders
    global mul
    global qty
    global dir
    
    global long_tp
    global short_tp
    long_tp = 0
    short_tp = 0
    long_orders = []
    short_orders = []
    mul = 0
    qty = 0
    dir = ''

    return redirect(url_for('home'))






## chain

### range : 
# long : abs(start / end)
# short : start / end 

## step:
### 1.积：等多空爆仓比出现明显大差距
### 2.选：选择合适排列，选择合适手数
###     （1）多空比1:1，  2倍杠杆
###     （2）多空比2:1，  4倍杠杆
###     （3）多空比3:1，  6倍杠杆
###     （4）多空比4:1，  8倍杠杆
### 3.排：根据排列排单


class FireChain:
    def __init__(self,long_start,long_end,short_start,short_end) -> None:
        self.pct_range = [4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]

        self.long_start = long_start
        self.long_end = long_end
        self.long_unit = 0
        self.long_unit_length = 0
        self.long_chains = []

        self.short_start = short_start
        self.short_end = short_end
        self.short_unit = 0
        self.short_unit_length = 0
        self.short_chains = []

    def get_chains(self):

        if self.long_start is not None and self.long_end is not None: # long
            start = self.long_start
            end = self.long_end
            pct_base = self.long_unit
            length = abs(start - end)
            p_base = max(abs(start),abs(end))
            c_base = round(p_base * pct_base)
            self.long_unit_length = c_base
            print(f"pct_base is : {pct_base} , base_length is {c_base}")
            c_times = round(length/c_base)
            print(f"opearate times : {c_times -1}")

            chains = []
            chains.append(start)
            for i in range(c_times):
                c_target_end = start + (i+1)*c_base
                chains.append(c_target_end)
            self.long_chains = chains
            
        if self.short_start is not None and self.short_end is not None: # short
            start = self.short_start
            end = self.short_end
            pct_base = self.short_unit
            length = abs(start - end)
            p_base = max(abs(start),abs(end))
            c_base = round(p_base * pct_base)
            self.short_unit_length = c_base
            print(f"pct_base is : {pct_base} , base_length is {c_base}")
            c_times = round(length/c_base)
            print(f"opearate times : {c_times -1}")

            chains = []
            chains.append(start)
            for i in range(c_times):
                c_target_end = start - (i+1)*c_base
                chains.append(c_target_end)
            print("let us make short orders !!")
            self.short_chains = chains
            

    def list_orders(self,pct_base,chains,dirc):
        pct_base = pct_base * 10000
        orders = []
        mul = 1.382
        order_times = len(chains)
        if dirc == 'long':
            dist = round(self.long_unit_length * mul)
            for i in range(order_times -2):
                base = chains[i+1]
                order = [base,base + dist,base - dist]
                orders.append(order)
                a = i+1
                exp_tp_pct = round((pct_base*(a-1)-3*(a+1))/10000,5)
                print(exp_tp_pct)
                exp_tp = exp_tp_pct * abs(chains[-1])
                print(f"the {i+1} order is : {order} , expect profit is {exp_tp}")
        if dirc == 'short':
            dist = round(self.short_unit_length * mul)
            for i in range(order_times -2):
                base = chains[i+1]
                order = [base,base - dist,base + dist]
                orders.append(order)
                a = i+1
                exp_tp_pct = round((pct_base*(a-1)-3*(a+1))/10000,5)
                print(exp_tp_pct)
                exp_tp = exp_tp_pct * abs(chains[-1])
                print(f"the {i+1} order is : {order} , expect profit is {exp_tp}")
        return orders


    def select_best_c_pct(self,start,end):
        start = start
        end = end
        length = abs(start - end)
        total_pct = round(length / start,5)
        print(f"total profit pct is {total_pct}")
        p_base = max(abs(start),abs(end))
        best_exp_pct = 0 
        best_exp_tp = 0

        for i in self.pct_range:
            i = round(i/10000,4)
            c_base = round(p_base * i)
            #print(f"pct_base is : {i} , base_length is {c_base}")
            c_times = round(length/c_base)
            op_times = c_times -1 
            #print(f"opearate times : {op_times}")
            exp_tp_pct = round((i*10000*(op_times-1)-3*(op_times+1))/10000,5)
            exp_tp = exp_tp_pct * abs(p_base)
            #print(f"expect profit pct is {exp_tp_pct} , profit is {exp_tp}")
            if exp_tp > best_exp_tp:
                best_exp_tp = exp_tp
                best_exp_pct = i
        expect_loss = (best_exp_pct + 0.0003) * abs(p_base)
        max_loss = expect_loss * op_times
        print(f"best profit is {best_exp_tp},best pct is {best_exp_pct} , expectloss is {expect_loss} , max loss is {max_loss}" )
        if start == self.long_start:
            self.long_unit = best_exp_pct
        elif start == self.short_start:
            self.short_unit = best_exp_pct
        return best_exp_tp

    ## inner chain ; strength chain
    ### 


    def select_best_multi(self,dex):
        long_length = self.long_chains[-1] - self.long_chains[0]
        short_length = self.short_chains[0] - self.short_chains[-1]
        base_qty = round(dex/self.short_chains[0],1)
        pct = round(long_length/short_length,2)
        if pct <=0.25 or pct >=4:
            mul = 8
            qty = base_qty*mul
            if pct >1:
                dir = 'long'
            else:
                dir = 'short'
            return mul,qty,dir
        
        elif pct <=0.33 or pct >= 3:
            mul = 6
            qty = base_qty*mul
            if pct >1:
                dir = 'long'
            else:
                dir = 'short'
            return mul,qty,dir
        
        elif pct <=0.5 or pct >= 2:
            mul = 4
            qty = base_qty*mul
            if pct >1:
                dir = 'long'
            else:
                dir = 'short'
            return mul,qty,dir
        
        elif pct <=1 or pct >= 1:
            mul = 2
            qty = base_qty*mul
            if pct >1:
                dir = 'long'
            else:
                dir = 'short'
            return mul,qty,dir



if __name__ == '__main__':
    app.run(debug=True, port=8080)

