import json
from typing import Dict


def clean_wordlist():
    with open("acc1_twitch_wordlist.json", "r") as f:
        word_list = json.loads(f.read())
    clean_wordlist = []
    for word in word_list:
        clean_word = "".join(char for char in word if char.isalpha())
        clean_wordlist.append(clean_word.lower())

    clean_wordlist = sorted(list(set(clean_wordlist)))

    with open("acc1_twitch_wordlist_clean.json", "w") as f:
        f.write(json.dumps(clean_wordlist, indent=4, sort_keys=True))


def merge_wordlist():
    merged_list = set()
    for file in ["acc2_twitch_wordlist.json", "acc1_twitch_wordlist.json"]:
        with open(file, "r") as f:
            file_content = f.read()
            json_content = json.loads(file_content)
            set_content = set(json_content)
            merged_list |= set_content

    with open("merged_wordlist.json", "w") as f:
        f.write(json.dumps(sorted(list(merged_list)), indent=4, sort_keys=True))


def process_english():
    with open("english_words_dictionary_raw.json", "r") as f:
        english_words_dict: Dict = json.loads(f.read())

    english_words = sorted(english_words_dict.keys())

    with open("english_words_dictionary.json", "w") as f:
        f.write(json.dumps(english_words, indent=4, sort_keys=True))


def merge_english_dictionary():
    with open("english_words_dictionary.json", "r") as f:
        dictionary_wordlist = set(json.loads(f.read()))

    with open("merged_wordlist.json", "r") as f:
        custom_wordlist = set(json.loads(f.read()))

    words_not_in_dictionary = custom_wordlist - dictionary_wordlist

    words_removed = custom_wordlist - words_not_in_dictionary
    print(words_removed)

    with open("custom_wordlist.json", "w") as f:
        f.write(
            json.dumps(sorted(list(words_not_in_dictionary)), indent=4, sort_keys=True)
        )


def get_users():
    with open("acc1_messages.json", "r") as f:
        message_list = json.loads(f.read())
    users = {}
    for username, data in message_list.items():
        users[username] = {
            "last_message": data[-1]["date"],
            "first_message": data[0]["date"],
            "messages": len(data),
        }
    with open("acc1_usernames.json", "w") as f:
        f.write(json.dumps(users, indent=4, sort_keys=True))


def blacklist_english_dictionary():
    with open("english_words_dictionary.json", "r") as f:
        dictionary_wordlist = set(json.loads(f.read()))

    with open("blacklisted_words.json", "r") as f:
        custom_wordlist = set(json.loads(f.read()))

    dictionary_cleaned = dictionary_wordlist - custom_wordlist

    # words_removed = custom_wordlist.union(dictionary_wordlist)
    # print(words_removed)

    with open("dictionary_cleaned.json", "w") as f:
        f.write(
            json.dumps(sorted(list(dictionary_cleaned)), indent=4, sort_keys=True)
        )

if __name__ == "__main__":
    pass
    # blacklist_english_dictionary()
    # get_users()
    # merge_english_dictionary()
    # process_english()
    # merge_wordlist()
    # clean_wordlist()
