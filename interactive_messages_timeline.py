import whatsapp_tools as wt
import plotly.express as px


file_path = '/home/pedro/Documentos/Codes/whatsapp_analysis/big_chat.txt'
messages = wt.parse_whatsapp_chat(file_path)
df = wt.count_each_sender_date(messages)
df = df.resample('W').sum()

# Limit the number of senders
top_10_senders = df.sum().nlargest(10).index
df = df[top_10_senders]

# Convert DataFrame to long format
df = df.reset_index()
df = df.melt(id_vars='Date', var_name='sender', value_name='num_messages')

for template in ["plotly_dark", "simple_white"]:
    # Create an interactive line plot
    fig = px.line(
        df,
        x='Date',
        y='num_messages',
        color='sender',
        template=template,
        title=template
        )

    # Customize the plot and axes
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Number of messages'
        )

    fig.update_xaxes(
        title_font=dict(size=20),
        tickfont=dict(size=15)
    )

    fig.update_yaxes(
        title_font=dict(size=20),
        tickfont=dict(size=15)
    )

    # Display the plot
    fig.show()
