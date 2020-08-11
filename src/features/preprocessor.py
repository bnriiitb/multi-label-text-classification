import re
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer
from src.data.constants import RE_PATTERNS, STOPWORDS, APOSTROPHE_MAP


class Preprocessor(object):

    def __init__(self):
        self.tokenizer = TweetTokenizer()
        self.lemmatizer = WordNetLemmatizer()

    @staticmethod
    def remove_dates(comment):
        """
        Removes date time and time zone information from the comments
        """
        comment = comment.lower()
        comment = re.sub(
            """(jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december)\s\d{1,2}\s\d{2,4}""",
            ' ', comment)
        comment = re.sub(
            """\d{1,2}\s(jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december)\s\d{2,4}""",
            ' ', comment)
        comment = re.sub("""\d{1,2}:\d{1,2}""", ' ', comment)
        comment = re.sub("""utc""", ' ', comment)
        comment = " ".join(comment.split())
        return comment

    def clean_text(self, comment):
        """
        This function receives comments and returns clean word-list
        """
        # convert comment to lower case
        comment = comment.lower()

        # remove \n (new line characters)
        comment = re.sub("\\n", " ", comment)

        # remove URLs
        comment = re.sub(
            r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''',
            " ", comment)

        # remove ip addresses
        comment = re.sub("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", " ", comment)

        # remove usernames
        comment = re.sub("\[\[.*\]", " ", comment)

        # remove date time and time zone
        comment = self.remove_dates(comment)

        # remove repeating characters in a word ex: abbbbcd ==> abcd
        pattern = re.compile(r"(.)\1{2,}", re.DOTALL)
        comment = pattern.sub(r"\1", comment)

        # remove repeating words ex: you said that that that ==> you said that
        comment = re.sub(r'(\W|^)(.+)\s\2', '', comment)

        # substitute regex patterns for vulgar words ex: f***k ==> fuck
        for target, patterns in RE_PATTERNS.items():
            for pat in patterns:
                comment = re.sub(pat, target, comment)

        # remove if there are any extra spaces in comment
        comment = " ".join(comment.split())

        # perform tokenization
        words = self.tokenizer.tokenize(comment)

        # (')aphostophe  replacement (ie)   you're --> you are
        words = [APOSTROPHE_MAP[word] if word in APOSTROPHE_MAP else word for word in words]

        comment = " ".join(words)
        # remove special chars
        comment = re.sub(r"[^a-z0-9!#\$%\^\&\*_\-,\.\'()\/ ]", ' ', comment)

        # perform lemmatization
        words = [self.lemmatizer.lemmatize(word, "v") for word in comment.split()]
        words = [w for w in words if not w in STOPWORDS]

        clean_sent = " ".join(words)
        # remove any non alphanum,digit character
        clean_sent = re.sub("\W+", " ", clean_sent)
        clean_sent = re.sub("  ", " ", clean_sent)
        return (clean_sent)


if __name__ == '__main__':
    pp = Preprocessor()
    print(pp.clean_text("*a-hem*... ""nigger nigger nigger, nigger nigger, nigger nigger."" Thank you. \n"))
