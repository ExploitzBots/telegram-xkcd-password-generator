import random
from xkcdpass import xkcd_password
from other import dbworker
from other.config import Config


# Used to decide whether to capitalize the whole world or not
def throw_random():
    return random.randint(0, 1)


def generate_weak_pwd():
    # 2 words, no separators between words
    config = Config()
    return xkcd_password.generate_xkcdpassword(wordlist=config.wordlist, numwords=2, delimiter="")


def generate_normal_pwd():
    # 3 words, no separators between words, second word is CAPITALIZED
    config = Config()
    words = xkcd_password.generate_xkcdpassword(wordlist=config.wordlist, numwords=3, delimiter=" ").split()
    return "{0}{1}{2}".format(words[0], str.upper(words[1]), words[2])


def generate_strong_pwd():
    # 3 words, random CAPITALIZATION, random number as separator between words
    config = Config()
    words = xkcd_password.generate_xkcdpassword(wordlist=config.wordlist, numwords=3, delimiter=" ").split()
    return "{word0}{randnum0}{word1}{randnum1}{word2}".format(word0=str.upper(words[0]) if throw_random() else words[0],
                                                              word1=str.upper(words[1]) if throw_random() else words[1],
                                                              word2=str.upper(words[2]) if throw_random() else words[2],
                                                              randnum0=random.randint(0, 9),
                                                              randnum1=random.randint(0, 9))


def generate_stronger_pwd():
    # Same as "strong", but using 4 words
    config = Config()
    words = xkcd_password.generate_xkcdpassword(wordlist=config.wordlist, numwords=4, delimiter=" ").split()
    return "{word0}{randnum0}{word1}{randnum1}{word2}{randnum2}{word3}" \
        .format(word0=str.upper(words[0]) if throw_random() else words[0],
                word1=str.upper(words[1]) if throw_random() else words[1],
                word2=str.upper(words[2]) if throw_random() else words[2],
                word3=str.upper(words[3]) if throw_random() else words[3],
                randnum0=random.randint(0, 9),
                randnum1=random.randint(0, 9),
                randnum2=random.randint(0, 9))


def generate_insane_pwd():
    # 4 words, second one CAPITALIZED, separators, prefixes and suffixes
    config = Config()
    words = xkcd_password.generate_xkcdpassword(wordlist=config.wordlist, numwords=4, delimiter=" ").split()
    return "{prefix}{word0}{separator1}{word1}{separator2}{word2}{suffix}" \
        .format(prefix=random.choice("!$%^&*-_+=:|~?/.;0123456789"),
                suffix=random.choice("!$%^&*-_+=:|~?/.;0123456789"),
                word0=words[0],
                word1=str.upper(words[1]),
                word2=words[2],
                separator1=random.choice(".$*;_=:|~?!%-+"),
                separator2=random.choice(".$*;_=:|~?!%-+"))


def generate_custom(user):
    config = Config()
    user = dbworker.get_person(user)
    words = [str.upper(word) if throw_random() else word for word in xkcd_password.generate_xkcdpassword(
        wordlist=config.wordlist, numwords=user["word_count"], delimiter=" ").split()
             ]
    # Generate password without prefixes & suffixes
    result_array = []
    for i in range(user["word_count"] - 1):
        result_array.append(words[i])
        result_array.append(random.choice(".$*;_=:|~?!%-+"))
    result_array.append(words[-1])
    _pwd = "".join(result_array)

    # Add prefixes/suffixes (if needed)
    if user["prefixes"]:
        password = "{prefix!s}{password}{suffix!s}".format(
            prefix=random.choice("!$%^&*-_+=:|~?/.;0123456789"),
            password=_pwd,
            suffix=random.choice("!$%^&*-_+=:|~?/.;0123456789")
        )
    else:
        password = _pwd
    return password
