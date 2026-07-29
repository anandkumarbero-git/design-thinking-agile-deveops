import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Sample data
days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
sales = [12, 19, 15, 22, 18, 25, 30]
temp = [30, 32, 31, 29, 28, 27, 26]

x = np.arange(1, 11)
y = np.array([2, 4, 1, 5, 7, 8, 6, 9, 10, 12])

pie_labels = ['Python', 'C++', 'Java', 'JavaScript']
pie_sizes = [40, 25, 20, 15]

random_data = np.random.randn(1000)
box_data = [np.random.normal(loc, 1, 100) for loc in [1, 2, 3, 4]]

df = pd.DataFrame({
    'A': np.random.randint(1, 10, 10),
    'B': np.random.randint(1, 10, 10),
    'C': np.random.randint(1, 10, 10),
    'D': np.random.randint(1, 10, 10)
})

fig, axes = plt.subplots(4, 2, figsize=(14, 18))
fig.suptitle('Common Data Visualization Charts', fontsize=18, fontweight='bold')

# Line chart
axes[0, 0].plot(days, temp, marker='o', color='royalblue')
axes[0, 0].set_title('Line Chart')
axes[0, 0].set_xlabel('Day')
axes[0, 0].set_ylabel('Temperature')

# Bar chart
axes[0, 1].bar(days, sales, color='seagreen')
axes[0, 1].set_title('Bar Chart')
axes[0, 1].set_xlabel('Day')
axes[0, 1].set_ylabel('Sales')

# Scatter plot
axes[1, 0].scatter(x, y, color='crimson')
axes[1, 0].set_title('Scatter Plot')
axes[1, 0].set_xlabel('X')
axes[1, 0].set_ylabel('Y')

# Pie chart
axes[1, 1].pie(pie_sizes, labels=pie_labels, autopct='%1.1f%%', startangle=90)
axes[1, 1].set_title('Pie Chart')

# Histogram
axes[2, 0].hist(random_data, bins=30, color='orange', edgecolor='black')
axes[2, 0].set_title('Histogram')
axes[2, 0].set_xlabel('Value')
axes[2, 0].set_ylabel('Frequency')

# Box plot
axes[2, 1].boxplot(box_data, labels=['A', 'B', 'C', 'D'])
axes[2, 1].set_title('Box Plot')
axes[2, 1].set_ylabel('Values')

# Heatmap
sns.heatmap(df, annot=True, cmap='YlGnBu', ax=axes[3, 0])
axes[3, 0].set_title('Heatmap')

# Hide last empty subplot
axes[3, 1].axis('off')

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.show()
