import config
from telethon.errors import *
from telethon.sync import TelegramClient
from telethon.utils import get_peer_id, resolve_id, get_display_name, get_peer
from collections import Counter
import os
from pathlib import Path
import json
from typing import List
import mass_data


def log_channel(client, channel_id, allow_overwrite=False):
    """Logs a Telegram channel to full-featured JSON.

    Args:
        client (TelegramClient): Instance of the active Telegram client.
        channel_id (chat-like): Any chat-like identifier, preferably channel ID as integer.
        allow_overwrite (bool, optional): Whether or not a given file should be overwritten. Defaults to False.

    Returns:
        bool: Success status for write operation.
    """

    if not os.path.isdir("logs/"):
        os.mkdir("logs/")

    if not can_connect(client, channel_id):
        print(f"Error: Could not connect to chat {channel_id}. Likely a private/banned server.")
        return False

    with client:
        channel_id = resolve_id(client.get_peer_id(channel_id))[0]
        channel_name = client.get_entity(channel_id).title

        if allow_overwrite == False:
            if os.path.exists(f"logs/{channel_id}.json") and Path(f'logs/{channel_id}.json').stat().st_size > 1000:
                print(f"File {channel_id}.json already exists, not overwriting.")
                return True

        with open(f"logs/{channel_id}.json", 'w') as f:
            print(f"Logging chat for {channel_name} at logs/{channel_id}.json...")
            f.write('[\n')
            for msg in client.iter_messages(channel_id):
                f.write(msg.to_json())
                f.write(",\n")

            f.seek(0, os.SEEK_END)              # seek to end of file
            f.seek(f.tell() - 2, os.SEEK_SET)   # go backwards 2 bytes            
            f.truncate()                        # crop off the remaining portion of the file (final 2 bytes)
            f.write("\n]")

    print(f"Successfully logged.")
    return True

def all_forward_sources(client, channel_id):

    if os.path.exists(f"logs/{channel_id}.json"):           # if a log file exists, prefer that over a fresh connection.
        return all_forward_sources_from_file(channel_id)

    if not can_connect(client, channel_id):
        print("Error: Could not connect. Likely a private/banned server. Returning empty Counter().")
        return Counter()

    forward_sources = []
    with client:
        for msg in client.iter_messages(channel_id):
            if msg.fwd_from:
                try:
                    forward_sources.append(msg.fwd_from.from_id.channel_id)
                except:
                    continue
        return forward_sources

def all_forward_sources_from_file(channel_id):
    """Typically (but not always) shouldn't be called directly. all_forward_sources() will call this function if a file exists."""
    forward_sources = []

    filepath = f"logs/{channel_id}.json"
    with open(filepath) as f:
        j = json.load(f)
        for message in j:
            #is_fwd is truthy if and only if fwd_from is not None
            is_fwd = message.get("fwd_from")

            #Conditions for a channel forward:
            is_forwarded_post = is_fwd and is_fwd.get("from_id") and is_fwd.get("from_id").get("_") == "PeerChannel"
            
            if is_forwarded_post:
                forward_sources.append(is_fwd.get("from_id").get("channel_id"))

    return forward_sources

def get_chat_name(client, channel_id):
    if not can_connect(client, channel_id):
        return "_inaccessible: private or banned"
    with client:
        return client.get_entity(channel_id).title

def get_chat_id(client, channel_identifier):
    return resolve_id(client.get_peer_id(channel_identifier))[0]

def can_connect(client, channel_id):
    """Crude connectivity test for a given server. Likely a better way to accomplish.

    Args:
        client (TelegramClient): Instance of the active telegram client containing API access information.
        chat (int): While an int is preferable (and *potentially* required for other functions), this can be any chat-like identifier.

    Returns:
        bool: True if the server can be connected to, false otherwise.
    """
    try:
        with client:
            if client.get_entity(channel_id):
                return True
    except:
        return False

def counter_from_list_of_ids(client, id_list):
    """Generates a Counter() of forwarded post sources from a list of channel IDs.
    If an existing .json log exists for provided channel ID, it will be used in place of a fresh scrape.


    Args:
        client (TelegramClient): Instance of the active telegram client containing API access information.
        list (List[int]): List of channel IDs.

    Returns:
        Counter: Counter of forwarded post sources across all channels in list.
    """
    count = Counter()

    id_list = list(set(id_list))        # pare id_list to unique values before iterating over them

    print(f"Checking {len(id_list)} from list..")

    with client:
        for index, channel in enumerate(id_list):
            filename = f"logs/{channel}.json"
            if os.path.exists(filename):
                print(f"Using existing log file logs/{channel}.json. If log file is out of date, update using log_chat(client, {channel}, allow_overwrite=true).")
                count.update(Counter(all_forward_sources_from_file(channel)))
            else:
                print(f"Scraping Channel ID: {channel}, {len(id_list)-(index + 1)} Remaining")
                count.update(all_forward_sources(client, channel))

    return count

def write_all_sources_to_file(id_list, output_filename):
    """Given a list of channel IDs, writes a Counter() to a text file.
    Should likely be merged with counter_from_list_of_ids().

    Args:
        id_list (List[chat-like]): List of chat-like identifiers, preferably ID numbers.
        output_filename (str): Output filename. Writes to pwd.

    Returns:
        bool: Success state of write operation.
    """
    all_sources = Counter()

    id_list = list(set(id_list))    # Ensure no duplicates are processed.

    for channel in id_list:
        try:
            all_sources.update(all_forward_sources_from_file(channel))
        except FileNotFoundError:
            print(f"logs/{channel}.json not found, skipping (this is generally due to a channel being removed by Telegram).")
            continue
    with open(output_filename, 'w') as f:
        for count in all_sources.most_common():
            f.write(f"{count[0]}: {count[1]}\n")

    return True


if __name__ == "__main__":

    # Example: log channels listed in config.test_ids to JSON and store sources of all forwarded posts in sources.txt.

    client = TelegramClient('session_id', config.api_id, config.api_hash)   # API ID/hash must be provided by end-user.

    for channel in config.test_ids:
        log_channel(client, channel, allow_overwrite=False)

    write_all_sources_to_file(config.test_ids, "sources.txt")