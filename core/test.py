# 导入需要的库
from bs4 import BeautifulSoup
import urllib.request
import datetime

# 设置请求头信息
headers = {'User-Agent': 'Mozilla/5.0'}

# 发送请求并获取响应
request = urllib.request.Request('https://www.investing.com/economic-calendar/', headers=headers)
response = urllib.request.urlopen(request)

# 解析响应内容
soup = BeautifulSoup(response, 'html.parser')
table = soup.find('table', id='economicCalendarData')
rows = table.find_all('tr', class_='js-event-item')

# 提取信息
for row in rows:
    time = row.find('td', class_='time').text
    #contry = row.find('td', class_='country').text
    title = row.find('td', class_='event').text  
    impact = row.find('td', class_='sentiment').get('data-img_key')
# 从row中获取国家
    country = row.find('td', class_='flagCur').find('span').get('title')
# 过滤为美元事件
    if country == 'United States' and impact == 'bull1':

        time = row.find('td', class_='time').text  
        title = row.find('td', class_='event').text
        
        #actual = row.find('td', class_='bold act').text
        forecast_td = row.find('td', class_='fore')
        forecast = forecast_td.text if forecast_td else "未公布"

        previous_td = row.find('td', class_='prev')
        previous = previous_td.text if previous_td else "未公布"
        actual_td = row.find('td', class_='bold act')
        actual = actual_td.text if actual_td else "未公布"

        print(time, title, actual,forecast, previous)