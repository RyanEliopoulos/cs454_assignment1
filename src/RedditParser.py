import re


class RedditParser:

    def __init__(self, posts: list, stock_symbols: list):
        self.posts: list = posts
        self.symbol_set: set = set(stock_symbols)
        # Building regex tools
        self.whitespace_re: re = self._build_whitespace_re()
        self.alpha_re: re = self._build_alpha_re()
        self.fullalpha_re: re = self._build_fullalpha_re()

    def _build_whitespace_re(self) -> re:
        """
        Builds the RE facilities for replace strings of whitespace with a single space
        """
        re.DOTALL = True  # dots should include whitespace characters
        pattern: re = re.compile(r'\s\s*')
        return pattern

    def _build_alpha_re(self) -> re:
        """
        Build the RE facilities to pull alphabetic substrings encased in nonalpha characters
        """
        # (Non-alpha char)* (alpha char)+ (non-alpha char)
        # In case a symbol is surrounded with punctuation.
        return re.compile(r'[^a-zA-Z]*([a-zA-Z]+)[^a-zA-Z]*')

    def _build_fullalpha_re(self) -> re:
        """ Build RE to check if a word is comprised entirely of alpha characters.
            Works to prevent duplicates otherwise created by alpha_re
        """
        return re.compile(r'^[a-zA-Z]+$')

    def _included_symbols(self, word_set: set) -> list:
        """
            Compares the word set against the stock symbols, returning a list
            of all symbols found within the set
        """
        found_symbols: list = []
        # Evaluating every word in the post
        for word in word_set:
            word = word.upper()  # matching 'word' case to that of the stock symbols
            if word in self.symbol_set:
                found_symbols.append(word)
        return found_symbols

    def _remove_nonalpha(self, word_list: list) -> list:
        """ Further breaks each post 'word' down in substrings split on
            non alpha characters
        """
        new_words: list = []
        for word in word_list:
            # First checking if the word is already fully alpha characters
            if self.fullalpha_re.match(word) is None:
                # Not fully alpha
                matchlist = self.alpha_re.findall(word)
                if matchlist:  # At least one substring (new word)
                    for match in matchlist:
                        new_words.append(match)
        word_list.extend(new_words)
        return word_list

    def parse(self) -> list:
        """ Processes the wsb posts provided at initialization.
        """

        hits: list = []  # Posts that include 1 or more stock symbols
        for post in self.posts:
            title: str = post['data']['title']
            body: str = post['data']['selftext']
            combined: str = f'{title} {body}'  # To include all words in the posting
            # Normalizing whitespace to single characters
            combined = self.whitespace_re.sub(' ', combined)
            # Splitting
            word_list: list = combined.split(' ')
            # Creating new substrings split on non alpha characters
            word_list = self._remove_nonalpha(word_list)
            # Eliminating duplicates
            word_set: set = set(word_list)
            # Determining symbols found within the post
            included_symbols: list = self._included_symbols(word_set)
            if included_symbols:
                post['included_symbols'] = included_symbols
                hits.append(post)
        return hits

