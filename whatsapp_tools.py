import re
import datetime
import pandas as pd
import matplotlib as mpl
from collections import Counter


def labels_in_latex():
    # Enable LaTeX rendering
    mpl.rcParams['text.usetex'] = True

    # Configuring LaTex font
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = ['Computer Modern']
    mpl.rcParams['font.size'] = 13
    mpl.rcParams['legend.fontsize'] = 13


def parse_whatsapp_chat(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Regex for whatsapp
    ios_pattern = (
        r'\[(\d{2}/\d{2}/\d{2,4}) (\d{2}:\d{2}:\d{2})\] '
        r'([^:]+): (.+)'
        )
    android_pattern = r'(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}) - ([^:]+): (.+)'
    poco_pattern = r'(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2}) - ([^:]+): (.+)'

    messages = []
    for line in lines:
        match = re.match(android_pattern, line)
        if match:
            date, time, sender, message = match.groups()
            messages.append((date, time, sender, message))
        else:
            match = re.match(ios_pattern, line)
            if match:
                date, time, sender, message = match.groups()
                messages.append((date, time, sender, message))
            else:
                match = re.match(poco_pattern, line)
                if match:
                    date, time, sender, message = match.groups()
                    messages.append((date, time, sender, message))

    return messages


def count_each_sender_date(messages):
    # Delete useless data and turns the list into a df
    messages = [(msg[0], msg[2]) for msg in messages]

    ds_df = pd.DataFrame(messages, columns=['Date', 'Sender'])

    original_group_name = ds_df.at[0, 'Sender']
    is_not_system_msg = ds_df['Sender'] != original_group_name
    ds_df = ds_df[is_not_system_msg].reset_index(drop=True)

    # Count the messages and pivot the sender level
    ds_df = ds_df.groupby(['Date', 'Sender']).size()
    ds_df = ds_df.unstack(fill_value=0)

    # Order by date
    ds_df.index = pd.to_datetime(ds_df.index, format='%d/%m/%Y')
    ds_df = ds_df.sort_index()

    return ds_df


def count_messages_by_sender(messages):
    senders = [msg[2] for msg in messages]
    sender_counts = Counter(senders)
    return sender_counts


def get_day_of_week(date_string):
    date = datetime.datetime.strptime(date_string, '%d/%m/%Y').date()
    return date.strftime('%A')


def get_hour(time_str):
    # Convert the string to a datetime object
    try:
        time_obj = datetime.datetime.strptime(time_str, '%H:%M:%S')
    except ValueError:
        time_obj = datetime.datetime.strptime(time_str, '%H:%M')
    # Extract the hour
    return time_obj.hour


def split_and_count(text, word):
    # Split the string using the pattern
    split_text = re.split(r'(\W)', text)
    # Remove empty strings from the result
    split_text = [token for token in split_text if token.strip()]
    count = split_text.count(word)
    return count


def word_frequency(messages, words, by='weekday', time_period=[8, 18]):

    # Delete system messages
    original_group_name = messages[0][2]
    messages = [msg for msg in messages if msg[2] != original_group_name]

    messages = [msg for msg in messages if 'a été ajouté·e' not in msg[3]]
    messages = [msg for msg in messages if 'a ajouté' not in msg[3]]

    # Grab only essential data and create dataframe
    if by == 'weekday':
        messages = [(msg[0], msg[3]) for msg in messages]
        messages_df = pd.DataFrame(messages, columns=['Date', 'Message'])

    elif by == 'hour':
        messages = [(msg[1], msg[3]) for msg in messages]
        messages_df = pd.DataFrame(messages, columns=['Time', 'Message'])
        messages_df['Time'] = messages_df['Time'].apply(get_hour)

        time_range = list(range(time_period[0], time_period[1]+1))
        messages_df = messages_df[messages_df['Time'].isin(time_range)]
        messages_df = messages_df.reset_index(drop=True)

    else:
        print("Error: by input must be a weekday or hour")
        return

    # Count the appearances of the words
    messages_df['Message'] = messages_df['Message'].str.lower()

    if isinstance(words, str):
        word = words.lower()

        messages_df[word] = messages_df['Message'].apply(
            lambda x: split_and_count(x, word))

    elif isinstance(words, list):
        words = [word.lower() for word in words]

        for word in words:
            messages_df[word] = messages_df['Message'].apply(
                lambda x: split_and_count(x, word))

    else:
        print("Error: Words input must be a string or a list of strings")
        return

    messages_df.pop('Message')

    if by == 'weekday':
        # Delete messages without any of the words
        messages_df = messages_df[
            (messages_df.drop(columns='Date') != 0).any(axis=1)]
        messages_df = messages_df.reset_index(drop=True)

        # Groups by the weekday
        messages_df['Date'] = messages_df['Date'].apply(get_day_of_week)
        messages_df = messages_df.groupby('Date').sum()

        # Reindex the DataFrame to order by weekday
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                         'Friday', 'Saturday', 'Sunday']
        messages_df = messages_df.reindex(weekday_order).dropna()

    elif by == 'hour':
        # Delete messages without any of the words
        messages_df = messages_df[
            (messages_df.drop(columns='Time') != 0).any(axis=1)]
        messages_df = messages_df.reset_index(drop=True)

        # Groups by the full hour
        messages_df = messages_df.groupby('Time').sum()

    return messages_df, by
