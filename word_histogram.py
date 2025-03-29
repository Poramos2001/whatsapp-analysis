import whatsapp_tools as wt
import matplotlib.pyplot as plt


def sum_of_last(df, n):
    sum = 0
    for i, column in enumerate(df.columns):
        if (i < n):
            sum += df[column]
        else:
            break
    return sum


file_path = '/path/to/your/file/example.txt'
messages = wt.parse_whatsapp_chat(file_path)
messages_df, category = wt.word_frequency(messages,
                                          words=["sim", 'mas', 'n'],
                                          by='weekday',
                                          )

# Plot the stacked graph
plt.style.use('seaborn-v0_8-colorblind')
_, ax = plt.subplots(figsize=(10, 6))

for i, column in enumerate(messages_df.columns):
    bottoms = sum_of_last(messages_df, i)

    bars = ax.bar(messages_df.index,
                  messages_df[column],
                  bottom=bottoms,
                  label=f'{column}: {messages_df[column].sum()} times')

    # Add the values inside the bars
    if isinstance(bottoms, int):
        bottoms = [0] * len(bars)
    else:
        bottoms = bottoms.tolist()

    for bar, bottom in zip(bars, bottoms):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2,
                bottom + height/2,
                height,
                ha='center',
                va='center',
                color='black',
                fontsize=10,
                fontweight='bold')

# Remove unnecessary spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Set labels and title
ax.set_xlabel(category.capitalize())
ax.set_ylabel('Count')
plt.legend(bbox_to_anchor=(1.03, 1), loc='upper left')
plt.tight_layout()
plt.show()
