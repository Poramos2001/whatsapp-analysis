import re
import os
import datetime
import pandas as pd
import matplotlib as mpl
from collections import Counter


def labels_in_latex():
    """
    Configures matplotlib to accept LaTeX equation formats in its titles and
    legends, setting the font as serif of size 13.
    """
    # Enable LaTeX rendering
    mpl.rcParams['text.usetex'] = True

    # Configuring LaTex font
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = ['Computer Modern']
    mpl.rcParams['font.size'] = 13
    mpl.rcParams['legend.fontsize'] = 13


def parse_whatsapp_chat(file_path):
    """
    Reads a txt file of a group chat and returns a list of tuples, each tuple
    contains, in order, date, time, sender, message.

    Parameters:
        file_path (str): The file path of the txt file, can be either a
            relative path, an absolute path or a pathlib Path Object.

    Returns:
        messages (list of tuples): Each tuple contains one message found in the
            file. The message is broken down according to one of the three
            following whatsapp regular expressions: iOS, Android or POCO.
            Each tuple has four elements: date, time, sender and message.
    """
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
    """
    Counts the number of messages sent by each user on each day.

    Parameters:
        messages (list of tuples): Each tuple contains one message broken down
            in the following elements: date, time, sender and message.

    Returns:
        ds_df (pd.dataframe): Indexed by dates and each column is one sender
            present in the input list. Each element is the number of messages
            sent by the sender that names the column in the rows date.
    """
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
    """
    Returns a Counter with the total number of messages sent by each sender.
    """
    senders = [msg[2] for msg in messages]
    sender_counts = Counter(senders)
    return sender_counts


def get_day_of_week(date_string):
    """
    Returns the day of the week corresponding to the input date string.
    """
    date = datetime.datetime.strptime(date_string, '%d/%m/%Y').date()
    return date.strftime('%A')


def get_hour(time_str):
    """
    Returns the hour present in the input time string.
    """
    # Convert the string to a datetime object
    try:
        time_obj = datetime.datetime.strptime(time_str, '%H:%M:%S')
    except ValueError:
        time_obj = datetime.datetime.strptime(time_str, '%H:%M')
    # Extract the hour
    return time_obj.hour


def count_word(text, word):
    """
    Counts the number of times the input word appears in the input text.
    """
    # Split the string using the pattern
    split_text = re.split(r'(\W)', text)
    # Remove empty strings from the result
    split_text = [token for token in split_text if token.strip()]
    count = split_text.count(word)
    return count


def get_time_range(time_period):
    """
    Returns the list of full hours in the 24h system between the two numbers
    given as input, starting by the first element and ending at the second.

        e.g. get_time_range([22, 3]) --> [22, 23, 0, 1, 2, 3]
             get_time_range([12, 15]) --> [12, 13, 14, 15]
    """
    # Check if the input is correct
    if len(time_period) != 2:
        raise ValueError("'time_period' must be a list of two integers.")

    elif not (isinstance(time_period[0], int)
              and isinstance(time_period[1], int)):
        raise TypeError("'time_period' must be a list of two integers.")

    elif (min(time_period) < 0 or max(time_period) > 23):
        raise ValueError("The values within the 'time_period' variable must be"
                         " between 0 and 23.")

    # Generate the return list
    if time_period[0] <= time_period[1]:
        return list(range(time_period[0], time_period[1]+1))
    else:
        return list(range(time_period[0], 24)).append(
                                            list(range(0, time_period[1])))


def word_frequency(messages,
                   words,
                   by='weekday',
                   time_period=[8, 18],
                   group_name=None):
    """
    Calculates how many times a single word or each word in an iterable of
    words appears in the messages of the input messages list. The number of
    appearances of each word is either grouped by the weekday or hour the
    messages it is in were sent. If chosen by hour, it will be grouped by every
    hour in the given time period, ignoring the other appearances.

    Parameters:
        messages (list of tuples): Each tuple contains one message broken down
            in the following elements: date, time, sender and message.

        words (many): The word(s) meant to be searched, this variable can be a
            variable or a list/tuple/range of variables of the following types:
            str, int, float, complex or bool.

        by ('weekday' or 'hour'): Sets if the word(s) will be grouped by
            weekday or full hour (ignoring minutes and seconds).

        time_period (list of two ints): The number of appearances of words will
            be calculated for each individual hour within the time period. For
            further information see whatsapp_tools.get_time_range docstring.

        group_name (str): The group name considered when deleting system
            messages, if none is provided, the default is using the first
            sender in the messages list.

    Returns:
        messages_df (pd.dataframe): A dataframe indexed either by hour or
            weekday (depending on the 'by' parameter), with one column for each
            entry in the 'words' parameter. Each element is the number of
            times the word that names the column was sent in the rows
            weekday/hour.

        by (str): Returns the 'by' input to facilitate histogram plotting.
    """
    # Delete system messages
    if group_name is None:
        group_name = messages[0][2]

    messages = [msg for msg in messages if msg[2] != group_name]
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

        time_range = get_time_range(time_period)
        messages_df = messages_df[messages_df['Time'].isin(time_range)]
        messages_df = messages_df.reset_index(drop=True)

    else:
        raise ValueError("The 'by' input must be 'weekday' or 'hour'")

    # Count the appearances of the words
    messages_df['Message'] = messages_df['Message'].str.lower()

    if isinstance(words, (str, int, float, complex, bool)):
        word = str(words)
        word = word.lower().strip()

        messages_df[word] = messages_df['Message'].apply(
            lambda x: count_word(x, word))

    elif isinstance(words, (list, tuple, range)):
        words = [str(word).lower().strip() for word in words]

        for word in words:
            messages_df[word] = messages_df['Message'].apply(
                lambda x: count_word(x, word))

    else:
        raise TypeError(
            "The 'words' input must be a variable or a list/tuple/range of "
            " variables of the following types: str, int, float, complex"
            " or bool.")

    messages_df.pop('Message')

    if by == 'weekday':
        # Groups by the weekday
        messages_df['Date'] = messages_df['Date'].apply(get_day_of_week)
        messages_df = messages_df.groupby('Date').sum()

        # Reindex the DataFrame to order by weekday
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                         'Friday', 'Saturday', 'Sunday']
        messages_df = messages_df.reindex(weekday_order).dropna()

    elif by == 'hour':
        # Groups by the full hour
        messages_df = messages_df.groupby('Time').sum()

    return messages_df, by


def occult_names(file_path, rewrite=True, occult_group=True, group_name=None):
    """
    Occults the names of the people who sent each message in a group chat .txt
    file. The name of each person will become 'Person x', with x going from 0
    to n-1, n being the number of senders in the file. The file can either be
    rewritten or crated a copy of. There is also a choice if you want to occult
    the group name or not.

    Parameters:
        file_path (str): The file path of the txt file, can be either a
            relative path, an absolute path or a pathlib Path Object.

        rewrite (bool): Sets if the file will be rewritten or not. If False,
            the function will create a new file in the same directory named
            Copy_of_{filename}.

        occult_group (bool): Sets if the group name will be occulted or not.
            If True, the group name will be changed to 'Group chat', else it
            will be left as it is and not changed with the other names.

        group_name (str): The name of the group to be changed or kept, if None,
            the name considered will be that of the first sender.
    """
    messages = parse_whatsapp_chat(file_path)
    senders = [msg[2] for msg in messages]

    if group_name is None:
        group_name = senders[0]

    # List the unique senders
    senders = list(set(senders))
    senders.remove(group_name)

    # Replace the sender and group names
    with open(file_path, 'r') as file:
        content = file.read()

    if occult_group:
        content = content.replace(group_name, "Group chat")

    for i, sender in enumerate(senders):
        content = content.replace(sender, f"Person {i}")

    # Write the modified content back to the file
    if not rewrite:
        directory_path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        file_name = "Copy_of_" + file_name
        file_path = os.path.join(directory_path, file_name)

    with open(file_path, 'w') as file:
        file.write(content)
