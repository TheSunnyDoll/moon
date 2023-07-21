import requests
from bs4 import BeautifulSoup

url = 'https://metrics.deribit.com/options/BTC'

# 请求网页
response = requests.get(url)
print(response)
soup = BeautifulSoup(response.text, 'html.parser')

# 找到最大痛点表格
table = soup.find('table', id='max-pain')

# 提取表格行 
rows = table.find_all('tr')

# 解析最后一行即最近一次数据
last_row = rows[-1]
cells = last_row.find_all('td')

# 打印输出
print(cells[0].text) # 日期
print(cells[1].text) # 价格
print(cells[2].text) # 开息
print(cells[3].text) # 收息