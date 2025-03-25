import whatsapp_tools as wt
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
mpl.use('TkAgg')


file_path = '/home/pedro/Documentos/Codes/whatsapp_analysis/big_chat.txt'
messages = wt.parse_whatsapp_chat(file_path)
df = wt.count_each_sender_date(messages)
df = df.resample('W').sum()

# Limit the number of senders
top_10_senders = df.sum().nlargest(10).index
df = df[top_10_senders]

wt.labels_in_latex()

# Create the plot
_, ax = plt.subplots(figsize=(15, 6))

# Plot each column
for column in df.columns:
    ax.plot(df.index, df[column], label=column)

# Customize the plot
ax.set_xticks(df.index)
ax.set_xticklabels(df.index, rotation=45)
ax.grid(True, alpha=0.7)
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
ax.set_xlabel('Data', fontsize=16)
ax.set_ylabel('Número de mensagens', fontsize=16)

# Set the major ticks to be at the start of each week
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Show the plot
plt.show()
