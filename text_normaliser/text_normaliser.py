# Implementation Note:
# In this implementation, we take a block of text and split it up on a word by word basis splitting on whitespace
# This method was chosen because it is easy in python to match parts of a long string using RegEx, but if we have 
# e.g 12*13, we can find this in the string.
# NOTE: I realised while (about halfway through) coding this I could have used re.findall and iterated through the terms 
# found and used text.replace on the found text, but this solution will work OK for purposes of this example. 
# Using re.findall means I could have searched for e.g [0-9]+\s*[/]\s*[0-9]+ to match when there are whitespaces 
# between certain symbols e.g 12 / 11 / 2014 will not be seen as a date in my implementation as we have already split
# on a per string level via whitespace, but would if we wrote a regex that captures the whitespacing component (\s*).
# If I were to do this again, I probably would use this method, but the current solution works fine given the context.
# Also things like ...,12,13,... will not be recognised in my implementation, you need spaces after the commas e.g ..., 12, 13, ...

# Get dependences
import re # For regular expressions
from collections import Counter # A handy counter function
with open('cmudict.dict.txt') as f: # Get the CMU dictionary
    CMUdict = dict(re.findall(r'(\S+)\s+(.+)', f.read()))

# If you want to use the Spell Checker (see spellcheck() function)
from spellchecker import SpellChecker
spell = SpellChecker()

# Some helper functions that aren't processing functions
# Function for mapping numbers into words, including support for ordinals. Will work up to order billions.
def num2words(num,ordinal=False):
    if ordinal:
        nums_0_19 = ['Zeroth','First','Second','Third','Fourth','Fifth','Sixth','Seventh','Eighth','Ninth','Tenth','Eleventh','Twelfth','Thirteenth','Fourteenth','Fifteenth','Sixteenth','Seventeenth','Eighteenth','Nineteenth']
    if not ordinal:
        nums_0_19 = ['Zero','One','Two','Three','Four','Five','Six','Seven','Eight','Nine','Ten','Eleven','Twelve','Thirteen','Fourteen','Fifteen','Sixteen','Seventeen','Eighteen','Nineteen']
    nums_20_90 = ['Twenty','Thirty','Forty','Fifty','Sixty','Seventy','Eighty','Ninety']
    nums_scales = {100: 'Hundred',1000: 'Thousand', 1000000: 'Million', 1000000000: 'Billion'}
    if num < 20:
        return nums_0_19[num]
    if num < 100:
        return nums_20_90[int(num/10)-2] + ('' if num%10 == 0 else ' ' + nums_0_19[num%10])
    # find the largest key smaller than num
    maxkey = max([key for key in nums_scales.keys() if key <= num])
    # The following uses recursion, note that between every power of 10 we include an and, but this could be changed
    # If there is extra processing afterwards like e.g the removal of stopwords/pronounciation this wont matter...
    if ordinal:
        word = num2words(int(num/maxkey)) + ' ' + nums_scales[maxkey] + ('' if num%maxkey == 0 else ' and ' + num2words(num%maxkey,ordinal=True))
        if word.endswith(('ed','nd','n','y')): # Account for edge cases like Twenty -> Ninety and Hundred -> Billion
            if word.endswith('y'):
                word = word[:-1] + 'ie' # Add 'ie' so that e.g twenty -> twentie (then add th afterwards as applies to all)
            word += 'th'
        return word
    if not ordinal:
        return num2words(int(num/maxkey)) + ' ' + nums_scales[maxkey] + ('' if num%maxkey == 0 else ' and ' + num2words(num%maxkey))

# Processing functions
def process_contractions(string):
    ''' Performs normalisation of contractions in the string
    One clear extension is a name dictionary lookup to see if the start of the string is a name, in which case we dont
    want to do the 's -> is substitution because of it is posessive not a contraction. However, this wont include all cases
    e.g naming of characters in books like Sergeant's or non standard names (not in dictionary) but we include it for now
    Inputs: s - a single string of input string
    --------------
    Outputs: Processed string - pstring'''
    pstring = re.sub(r"n\'t", " not", string) #n't -> not
    pstring = re.sub(r"\'re", " are", pstring) #'re -> are
    pstring = re.sub(r"\'s", " is", pstring) #'s -> is (BE CAREFUL OF POSESSIVE NOUNS e.g Ryan's -X-> Ryan is)
    pstring = re.sub(r"\'d", " would", pstring) #'d -> would
    pstring = re.sub(r"\'ll", " will", pstring) #'ll -> will
    pstring = re.sub(r"\'ve", " have", pstring) #'ve -> have
    pstring = re.sub(r"\'m", " am", pstring) #'m -> am
    return pstring

def process_pronounciation(string,country='US'):
    ''' Performs normalisation of pronounciation in the string
    Inputs: string - a single string of input string
            country - A country in {UK (Default),US} that determines the pronounciation
    --------------
    Outputs: Processed string - pstring '''
    # Take care of any trailing punctuation
    string, endstring = trailing_punctuation(string)
    if country == 'UK':
        # Could find another pronounciation dictionary for UK pronounciation if we wanted to. I couldnt find any 
        # (good ones) online after a brief search
        return string + endstring
    elif country == 'US':
        if string in CMUdict.keys():
            return CMUdict[string] + endstring
        else: # If string is not in CMUdict we have to decide whether or not to delete it from text etc...
            return '' + endstring

def process_numbers(string):
    ''' Performs normalisation of numbers in the string as well as multiplications e.g 12*13 = twelve times 13
    divisions e.g 14/5 -> fourteen divided by five and decimal points e.g 67.98 -> sixty seven point nine eight
    Inputs: string - a single string of input string
    --------------
    Outputs: Processed string'''
    # Take care of any trailing punctuation
    string, endstring = trailing_punctuation(string)
    # Take care of cases where numbers are ordinals
    ords = ('0th','1st','2nd','3rd','4th','5th','6th','7th','8th','9th','10th','11th','12th','13th')
    if string.endswith(ords):
        pstring = string[:-2] # Strip off the th/st/nd
        return num2words(int(pstring),ordinal=True) + endstring

    # Take care of cases where its numbers that are multiplied together as strings
    if re.match(r"[0-9]+[*][0-9]+",string): # Matches cases like e.g. 12*13
        pstring = string.split("*")
        return ' times '.join([num2words(int(s)) for s in pstring]) + endstring
    elif re.match(r"[0-9]+[x][0-9]+",string): # Matches cases like e.g. 12x13
        pstring = string.split("x")
        return ' times '.join([num2words(int(s)) for s in pstring]) + endstring
    elif re.match(r"[0-9]+[X][0-9]+",string): # Matches cases like e.g. 12X13
        pstring = string.split("X")
        return ' times '.join([num2words(int(s)) for s in pstring]) + endstring

    # Take care of cases where its numbers that are divided as strings
    elif re.fullmatch(r"[0-9]+[/][0-9]+",string): # Matches cases like e.g. 12/13 (use fullmatch so no ambiguity e.g 12/3/4)
        pstring = string.split("/")
        return ' divided by '.join([num2words(int(s)) for s in pstring]) + endstring

    # Take care of cases where it is *just* a number
    elif re.fullmatch(r"[0-9]+",string): #If the string matches just a number then return the number as words
        return num2words(int(string)) + endstring

    # Take care of cases involving a decimal point
    elif re.match(r"[0-9]+[.][0-9]+",string): # Matches cases like e.g. 12.13
        pstring = string.split(".")
        # The below is because we say twelve point one three not twelve point thirteen
        return num2words(int(pstring[0])) + ' point ' + ' '.join([num2words(int(s)) for s in pstring[1]]) + endstring

    # Take care of cases where there have been spaces between the times signs
    # Note that we dont do this for a single x -> times as this would be ambiguous given my implementation
    # (see note at top) That is, 12 x 13 will NOT be corrected to 12 times 13
    elif string == '*':
        return 'times'
    
    # The string didn't match any of the regex, so leave it unchanged
    else:
        return string + endstring

def process_times(string):
    ''' Performs normalisation of times in the string e.g 10:35 = ten thirty five
    Note that exact hours like 15:00 -> fifteen zero in this implementation, which isnt what we say in english. Could easily be changed to
    something like fifteen o clock or three o clock or three pm or whatever - it depends on what we want and would just require some more if statements
    Inputs: string - a single string of input text
    --------------
    Outputs: Processed string - pstring '''
    # Take care of any trailing punctuation
    string, endstring = trailing_punctuation(string)

    if re.match(r"[0-9]{1,2}[:][0-9]{2}[:][0-9]{2}",string): # Will match things like 10:35:07
        pstring = string.split(":")
        if pstring[-1].endswith(('am','pm','AM','PM','a.m','a.m.','p.m','p.m.')): # Takes care of cases where am/pm is attached to date without a space
            pstring.append(pstring[-1][2:])
            pstring[2] = pstring[2][:2]
            return num2words(int(pstring[0])) + ' ' + num2words(int(pstring[1])) + ' and ' + num2words(int(pstring[2])) + ' seconds ' + pstring[3] + endstring
        else:
            return num2words(int(pstring[0])) + ' ' + num2words(int(pstring[1])) + ' and ' + num2words(int(pstring[2])) + ' seconds' + endstring
            
    elif re.match(r"[0-9]{1,2}[:][0-9]{2}",string): # Will match things like 10:35
        pstring = string.split(":")
        if pstring[-1].endswith(('am','pm','AM','PM','a.m','a.m.','p.m','p.m.')): # Takes care of cases where am/pm is attached to date without a space
            pstring.append(pstring[-1][2:])
            pstring[1] = pstring[1][:2]
            return num2words(int(pstring[0])) + ' ' + num2words(int(pstring[1])) + ' ' + pstring[2] + endstring
        else:
            return num2words(int(pstring[0])) + ' ' + num2words(int(pstring[1])) + endstring

    else: # None of the regex was matched, so return the string
        return string + endstring

def process_dates(string,country='UK'):
    ''' Performs normalisation of dates in the string e.g 01/07/2015 = first july two thousand and fifteen
    Note there are two formats: DDMMYY(YY) and MMDDYY(YY)
    Note that for dates num2words will do 1996 -> one thousand nine hundred and ninety six not nineteen ninety six
    This could be changed if it was felt necessary.
    I havent been too strict on the regex e.g forcing Days in {1,...,31} and Months in {1,...,12}, and this could be changed if necessary
    but we note that the code will error as it is calling ords and months...
    Inputs: string - a single string of input text
            country - A country in {UK (Default),US} that determines the date format (see above)
    --------------
    Outputs: Processed string - pstring '''
    # Take care of any trailing punctuation
    string, endstring = trailing_punctuation(string)
    # Define the names of months (put empty string in 0th place for nicer indexing later on)
    months = ['','January','February','March','April','May','June','July','August','September','October','November','December']
    # Define the names of ordinals
    ords = ['zeroth','first','second','third','fourth','fifth','sixth','seventh','eighth','ninth','tenth','eleventh',
            'twelfth','thirteenth','fourteenth','fifteenth','sixteenth','seventeenth','eighteenth','nineteenth','twentieth',
            'twenty first','twenty second','twenty third','twenty fourth','twenty fifth','twenty sixth','twenty seventh','twenty eigth','twenty ninth','thirtieth', 
            'thirty first']

    if country == 'UK': #Format is then  DDMMYY(YY)
        if re.match(r"[0-9]{1,2}[\\][0-9]{1,2}[\\][0-9]{2}([0-9]{0}|[0-9]{2})",string): # Matches D(D)\M(M)\YY(YY)
            pstring = string.split("\\")
            return ords[int(pstring[0])] + ' of ' + months[int(pstring[1])] + ' ' + num2words(int(pstring[2])) + endstring
        elif re.match(r"[0-9]{1,2}[/][0-9]{1,2}[/][0-9]{2}([0-9]{0}|[0-9]{2})",string): # Matches D(D)/M(M)/YY(YY)
            pstring = string.split("/")
            return ords[int(pstring[0])] + ' of ' + months[int(pstring[1])] + ' ' + num2words(int(pstring[2])) + endstring
        elif re.match(r"[0-9]{1,2}[-][0-9]{1,2}[-][0-9]{2}([0-9]{0}|[0-9]{2})",string): # Matches D(D)-M(M)-YY(YY)
            pstring = string.split("-")
            return ords[int(pstring[0])] + ' of ' + months[int(pstring[1])] + ' ' + num2words(int(pstring[2])) + endstring
        else: # The string didn't match any regex, so leave it unchanged
            return string + endstring

    elif country == 'US': #Format is then MMDDYY(YY)
        if re.match(r"[0-9]{1,2}[\\][0-9]{1,2}[\\][0-9]{2}([0-9]{0}|[0-9]{2})",string): # Matches M(M)\D(D)\YY(YY)
            pstring = string.split("\\")
            return ords[int(pstring[1])] + ' of ' + months[int(pstring[0])] + ' ' + num2words(int(pstring[2])) + endstring
        elif re.match(r"[0-9]{1,2}[/][0-9]{1,2}[/][0-9]{2}([0-9]{0}|[0-9]{2})",string): # Matches M(M)/D(D)/YY(YY)
            pstring = string.split("/")
            return ords[int(pstring[1])] + ' of ' + months[int(pstring[0])] + ' ' + num2words(int(pstring[2])) + endstring
        elif re.match(r"[0-9]{1,2}[-][0-9]{1,2}[-][0-9]{2}([0-9]{0}|[0-9]{2})",string): # Matches M(M)-D(D)-YY(YY)
            pstring = string.split("-")
            return ords[int(pstring[1])] + ' of ' + months[int(pstring[0])] + ' ' + num2words(int(pstring[2])) + endstring
        else: # The string didn't match any regex, so leave it unchanged
            return string + endstring

def remove_punctuation(string):
    ''' Removes punctuation from a string efficiently (string.translate is slightly quicker than RegEx)'''
    punctuation = '''!()-[]{};:'"\,<>./?@#$%^&*_~''' # Define punctuation symbols
    return string.translate(str.maketrans('','',punctuation)) # i.e translating punctuation -> ''

def trailing_punctuation(string):
    ''' Removes 'trailing' punctuation from a string
    Outputs: string, endstring -> string is the string without trailing punctuation (endstring)'''
    punctuation = '''!()-[]{};:'"\,<>./?@#$%^&*_~''' # Define punctuation symbols
    endstring = ''
    if string in punctuation:
        return string, endstring
    else:
        i=0
        while True:
            if string[::-1][i] in punctuation: # Note we have reversed the string
                endstring += string[::-1][i]
                i +=1
            else:
                break
        if len(endstring) > 0:
            return string[:-len(endstring)],endstring
        else:
            return string, endstring

def spellcheck(string):
    ''' One 'Pure Python' way to do this is via a Norvig spellcheck of the string 
    (theory found by reading http://norvig.com/spell-correct.html) but when implemented this code was found to be
    INCREDIBLY slow on my machine. Another way is to make use of GitHub. I use https://github.com/barrust/pyspellchecker
    This repo essentially uses Norvig's technique.
    If you want to run this code, please pip install pyspellchecker and see the GitHub repo for instructions.
    Note that it can still be quite slow to run depending on the circumstance. The below example code should run instantly.
    Inputs: string - a single string of input text
    --------------
    Outputs: Processed string - a single string of processed string '''
    # Take care of any trailing punctuation
    string, endstring = trailing_punctuation(string)
    if string in CMUdict.keys(): # Check if the string is in the dictionary, if it is then it is spelled correctly
        return string + endstring
    else: # we need to correct the spelling of the string, and we use pyspellchecker
        return spell.correction(string) + endstring

def process_text(text,pronounciation=False, punctuation=True, spellchecking=False):
    # Run it through the functions defined above
    text = text.lower() # Make sure the text is all lowercase for standardisation
    text = text.split() # Split the text
    text = [process_contractions(string) for string in text]
    text = [process_dates(string) for string in text]
    text = [process_numbers(string) for string in text]
    text = [process_times(string) for string in text]
    text = [word.lower() for word in text] # Make lowercase again since some replacements included capital letters
    text = ' '.join([s for s in text]) # Join up all the partitions after processing (some contain lists of lists)
    text = text.split() # Split for the below procedures so now list of strings
    if spellchecking: # OPTIONAL: Perform spellchecking
        text = [spellcheck(string) for string in text] 
    if pronounciation: # OPTIONAL: Convert to pronounciation format
        text = [process_pronounciation(string) for string in text]
    text = ' '.join([s for s in text]) # Join up all the partitions after processing
    if not punctuation: # OPTIONAL: Remove punctuation, so if punctuation=True there is punctuation
        text = remove_punctuation(text)
    return text 

if __name__ == '__main__':
    # Define some sample text to test the function
    text = '''Here I have some sample text to test my code! There are some numbers like 13 and 28 
            as well as products of numbers like 4 * 2, 17*13 and 24x12 and also divisions like 14/5. 
            Here are some important dates: 01/12/2000 and 12-02-2018. We also have some times in the day, 
            like I eat lunch at 12:35pm and go to the gym at 15:30. At the gym, I did a run that lasted 10:14:35. 
            We include support for decimals like 12.1356 and ordinals like 1st and 415th.
            It can also do contractions, like I'm sorry I couldn't make it tonight, I'll try again next week.
            There is also spell check support, so it will correct wrods.'''

    # Process the text
    out_text = process_text(text)

    # Print the output
    print(out_text)

    # Do different variations
    out_text = process_text(text,pronounciation=False,punctuation=False)
    print(out_text)
    out_text = process_text(text,pronounciation=True,punctuation=True)
    print(out_text)
    out_text = process_text(text,pronounciation=False,punctuation=False,spellchecking=True)
    print(out_text)