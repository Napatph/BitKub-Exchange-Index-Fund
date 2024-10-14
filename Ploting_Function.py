import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('crypto_index.csv')

df['Timestamp'] = pd.to_datetime(df['Timestamp'])

plt.figure(figsize=(10, 5))
plt.plot(df['Timestamp'], df['Normalized Index'], marker='o', linestyle='-', linewidth=2)
plt.xlabel('Timestamp')
plt.ylabel('Normalized Index')
plt.title('Normalized Index over Time')
plt.grid(True)

plt.show()