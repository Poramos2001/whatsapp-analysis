import pandas as pd
import whatsapp_tools as wt


def main():
    file_path = '/path/to/your/file/example.txt'
    messages = wt.parse_whatsapp_chat(file_path)
    sender_counts = wt.count_messages_by_sender(messages)

    total_messages = sum(sender_counts.values())

    top_10_senders = sender_counts.most_common(10)
    df_top_10_senders = pd.DataFrame(top_10_senders,
                                     columns=['Sender', 'Message Count'])

    df_top_10_senders['Message Ratio'] = (df_top_10_senders['Message Count']
                                          / total_messages)
    return df_top_10_senders, total_messages


df_top_10_senders, total_messages = main()

# Display the results
print(f'Total of messages: {total_messages}')
print(df_top_10_senders)
