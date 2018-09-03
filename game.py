#Check if user move was valid by checking if words exist given the last user given letter
#Check if user won
#Computer choice (very very hard to beat as a human) to win:
# - Word must be X letters or longer (default 5)
# - Word must be one letter longer than previous word
#If there are no words that match this pattern to play a single letter but win later:
# - Find words three letters longer than previous word (*)
# - Exclude words that exist with two more letters than previous word
# - If there are no words that match this criteria, try with +2 letters combination
#If there are no words at step (*) then the human will probably win :(

import http.client
import json
import sys
from random import shuffle

game_winner = "nobody"
conn = http.client.HTTPSConnection("api.datamuse.com")
current_word = ""
min_word_len = 5 # >4 is recommended to get the best results out of the dictionary

while game_winner is "nobody":
    
    #User input
    letter = ""
    if(len(current_word) > 0):
        print("The current word is " + current_word)
    while len(letter) != 1:
        letter = input("Enter your next letter: ")
        if len(letter) > 1:
            print("Do I need to explain what a single letter is? Cmon bro.")
    current_word += letter

    conn.request("GET", "/words?sp=" + current_word + "&max=1")
    r = conn.getresponse()
    if r.status != 200 or r.reason != "OK":
        print("Could not reach the word api (" + r.status + " " + r.reason + ")")
        sys.exit(1)
    data = r.read()
    parsed_data = json.loads(data)
    
    if bool(parsed_data) and parsed_data[0]["word"] == current_word and len(current_word) >= min_word_len:
        game_winner = "human"
        break

    #Verify user input
    conn.request("GET", "/words?sp=" + current_word + "*&max=1")
    r = conn.getresponse()
    if r.status != 200 or r.reason != "OK":
        print("Could not reach the word api (" + r.status + " " + r.reason + ")")
        sys.exit(1)
    data = r.read()
    parsed_data = json.loads(data)

    if not bool(parsed_data):
        print("Fucking noob, looks like there are no words started with " + current_word + ".")
        game_winner = "cpu"
        break
    
    #Computer attempt to win
    if len(current_word) >= min_word_len - 1:
        conn.request("GET", "/words?sp=" + current_word + "?&max=1")
        r = conn.getresponse()
        if r.status != 200 or r.reason != "OK":
            print("Could not reach the word api (" + r.status + " " + r.reason + ")")
            sys.exit(1)
        data = r.read()
        parsed_data = json.loads(data)
         
        if bool(parsed_data): #If word is found, then the cpu wins.
            shuffle(parsed_data)
            winning_word = parsed_data[0]["word"]
            winning_letter = winning_word.replace(current_word,"")
            current_word += winning_letter
            print("Computer played letter '" + winning_letter + "', winning the game with the word '" + current_word + "'")
            game_winner = "cpu"
            break
    
    #Computer play a letter
    letter = ""
    conn.request("GET", "/words?sp=" + current_word + "*&max=1000")
    r = conn.getresponse()
    if r.status != 200 or r.reason != "OK":
        print("Could not reach the word api (" + r.status + " " + r.reason + ")")
        sys.exit(1)
    data = r.read()
    parsed_data = json.loads(data)
    possible_words = [sublists.get('word') for sublists in parsed_data]
    possible_words.sort(key = len)
    chosen_word = ""
    
    for word in possible_words:
        chosen_word = word
        if (len(word)-len(current_word)) % 2 is not 1 or len(word) < min_word_len: #Word is not a possible word for the cpu
            continue
        valid = True
        for avoid_word in possible_words:
            if len(avoid_word) is len(word):
                break
            if (len(avoid_word)-len(current_word)) % 2 is 0 and word.startswith(avoid_word) and len(avoid_word) >= min_word_len: #Word is a threat word for the cpu
                valid = False
                break
        if valid:
            letter = word.replace(current_word,"")[0]
            break
    
    if letter:
        print("Computer played letter '" + letter + "', chosen word was '" + chosen_word + "'")
        current_word += letter
    else:
        shuffle(possible_words)
        for word in possible_words:
            if len(word) > len(current_word):
                letter = word.replace(current_word,"")[0]
                break
        if letter:
            print("Computer played letter '" + letter + "', randomized word was '" + chosen_word + "'")
            current_word += letter
        else:
            print("Something is wrong, could not find a word")


if game_winner is "cpu":
    print("HA! Fuck you, you lose.")

if game_winner is "human":
    print("Wtf dude, looks like '" + current_word + "' is a valid word, which means you win. Impressive.")