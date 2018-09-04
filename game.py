# General Flow of the Program:
# 
# 1- Check if user move was valid by checking if words exist given the last user given letter
# 2- Check if user won
# 3- Computer attempts to win by finding a word:
#     - Word must be X letters or longer (default 5)
#     - Word must be one letter longer than previous word
# 4- If there are no words that match this pattern yet, computer attempts to play a single letter from a word which will allow it to win later:
#     - Find words that the CPU can use to win (*)
#     - Exclude words that the human might use to win
# 5- If there are no words at step (*), play the next letter from a random word. If this point is reached, the human actually has a chance to win :(

import http.client
import json
import sys
from random import shuffle

game_winner = "nobody"
conn = http.client.HTTPSConnection("api.datamuse.com")
current_word = ""
min_word_len = 5 # >4 is recommended to get the best results out of the dictionary

def makeJSONAPIRequest(req) :
    conn.request("GET", req)
    r = conn.getresponse()
    if r.status != 200 or r.reason != "OK":
        print("Damn, could not reach the word api (" + r.status + " " + r.reason + ")")
        sys.exit(1)
    data = r.read()
    parsed_data = json.loads(data)
    return parsed_data

print("Let's play! Good luck, you'll need it. Minimum word length is " + str(min_word_len) + ".")

while game_winner is "nobody":
    
    #User input
    letter = ""
    if(len(current_word) > 0):
        print("The current word is " + current_word)
    while len(letter) != 1 or not letter.isalpha():
        letter = input("Enter your next letter: ")
        if len(letter) > 1:
            print("Do I need to explain what a single letter is? Cmon bro.")
        if not letter.isalpha():
            print("Nice try pentester, alphabetic characters only.")
    current_word += letter

    #Check if user won by completing a full word larger than the minimum size required
    parsed_data = makeJSONAPIRequest("/words?sp=" + current_word + "&max=1")
    
    if bool(parsed_data) and parsed_data[0]["word"] == current_word and len(current_word) >= min_word_len:
        game_winner = "human"
        break

    #Check if user lost by playing a letter from which no words can be formed
    parsed_data = makeJSONAPIRequest("/words?sp=" + current_word + "*&max=1")

    if not bool(parsed_data):
        print("Looks like there are no words started with " + current_word + ".")
        game_winner = "cpu"
        break
    
    #Computer attempt to find a winning letter
    if len(current_word) >= min_word_len - 1:
        parsed_data = makeJSONAPIRequest("/words?sp=" + current_word + "?&max=1")
         
        if bool(parsed_data): #If word is found, then the cpu wins.
            shuffle(parsed_data)
            winning_word = parsed_data[0]["word"]
            winning_letter = winning_word.replace(current_word,"")
            current_word += winning_letter
            print("Computer played letter '" + winning_letter + "', winning the game with the word '" + current_word + "'")
            game_winner = "cpu"
            break
    
    #Computer could not find a winning word just yet, so attempts to play a letter which will allow it to win later
    letter = ""
    parsed_data = makeJSONAPIRequest("/words?sp=" + current_word + "*&max=1000")
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
    
    # If a future winning word is found, then play the next letter of that word. Otherwise, play the next letter of a random word
    if letter:
        print("Interesting move. The computer played letter '" + letter + "'.")
        current_word += letter
    else:
        shuffle(possible_words)
        for word in possible_words:
            if len(word) > len(current_word):
                letter = word.replace(current_word,"")[0]
                break
        if letter:
            print("Nice one. Computer played letter '" + letter + "'.")
            current_word += letter
        else:
            print("Congratulations, you just found a bug. Could not find a word.")


if game_winner is "cpu":
    print("Computer wins, you lose.")

if game_winner is "human":
    print("Looks like '" + current_word + "' is a valid word, which means you win.")