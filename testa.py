import matplotlib.pyplot as plt
import pandas as pd

# Чтение данных из файла
data = pd.read_csv('btc.price', sep=' ', header=None, names=['Date', 'Price'])
# Преобразование колонки 'Date' в формат даты
data['Date'] = pd.to_datetime(data['Date'])

# Создание графика
plt.figure(figsize=(10, 6))
plt.plot(data['Date'], data['Price'], marker='o', linestyle='-', color='b', label='Bitcoin Price')
plt.xlabel('Date')
plt.ylabel('Price')
plt.title('Bitcoin Price Changes')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()

# Сохранение графика в файл
plt.savefig('bitcoin_price_chart.png')

# Отображение графика
plt.show()
