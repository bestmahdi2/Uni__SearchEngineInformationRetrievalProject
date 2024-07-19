import os
import re
import string
from time import sleep

import hazm


class Phase1:
    """
        Class for text preprocessing tasks such as normalization, tokenization, removing stopwords, lemmatization, and stemming.
    """

    PERSIAN_PUNCTUATION = ''.join(['«', '»', '×', '،', '؛', '؟', 'ـ', '٪', '٫', '٬'])

    def __init__(self) -> None:
        """
            Initializes Phase1 object with necessary resources and parameters.
        """
        self.informal_normalizer = hazm.InformalNormalizer(seperation_flag=True)
        self.normalizer = hazm.Normalizer(correct_spacing=True, remove_diacritics=True, remove_specials_chars=True,
                                          decrease_repeated_chars=True, persian_style=True, persian_numbers=True,
                                          seperate_mi=True)
        self.tokenizer = hazm.WordTokenizer(join_verb_parts=True, replace_links=True, replace_emails=True,
                                            replace_ids=True, replace_numbers=True, replace_hashtags=True)
        self.lemmatizer = hazm.Lemmatizer()
        self.stemmer = hazm.Stemmer()
        self.stopwords = Phase1.read_stopwords("Phase1/Stopwords")
        self.state = [0, "Not Started Yet!", '']
        self.punctuation_pattern = re.compile(f'[{re.escape(string.punctuation)}{self.PERSIAN_PUNCTUATION}]+')

    @staticmethod
    def read_stopwords(files_path) -> dict:
        """
            Reads stopwords from files and returns a dictionary.

            Args:
                files_path (str): Path to the directory containing stopwords files.

            Returns:
                dict: Dictionary containing stopwords.
        """

        stopwords = {}
        files = os.listdir(files_path)
        for file_name in files:
            with open(os.path.join(files_path, file_name), 'r', encoding='utf-8') as f:
                stopwords[file_name[:-4]] = [word.strip('‏') for word in f]

        return stopwords

    def informal_normalize(self, input_text: str) -> list[list[list[str]]]:
        """
            Normalizes informal text.

            Args:
                input_text (str): Input text to be normalized.

            Returns:
                list: Normalized text.
        """

        return self.informal_normalizer.normalize(input_text)

    def normalize(self, input_text: str) -> str:
        """
            Normalizes text.

            Args:
                input_text (str): Input text to be normalized.

            Returns:
                str: Normalized text.
        """

        return self.normalizer.normalize(input_text)

    def token_spacing(self, input_list: list) -> list:
        """
            Performs token spacing.

            Args:
                input_list (list): List of input tokens.

            Returns:
                list: List of tokens with correct spacing.
        """

        return self.normalizer.token_spacing(input_list)

    def tokenize(self, input_text: str) -> list:
        """
            Tokenizes input text.

            Args:
                input_text (str): Input text to be tokenized.

            Returns:
                list: List of tokens.
        """

        return self.tokenizer.tokenize(input_text)

    def lemmatize(self, input_text: str) -> str:
        """
            Lemmatizes input text.

            Args:
                input_text (str): Input text to be lemmatized.

            Returns:
                str: Lemmatized text.
        """

        return self.lemmatizer.lemmatize(input_text)

    def stem(self, input_text: str) -> str:
        """
            Stems input text.

            Args:
                input_text (str): Input text to be stemmed.

            Returns:
                str: Stemmed text.
        """

        return self.stemmer.stem(input_text)

    def remove_string_stopwords(self, input_text: list, stopword_dict='Mazdak') -> list:
        """
            Removes stopwords from input text.

            Args:
                input_text (list): List of input tokens.
                stopword_dict (str, optional): Dictionary name containing stopwords. Defaults to 'Mazdak'.

            Returns:
                list: Input text with stopwords removed.
        """

        stopwords = self.stopwords[stopword_dict]
        input_text = [i for i in input_text if i not in stopwords]

        return input_text

    def remove_punctuations(self, input_list: list) -> list:
        """
            Removes punctuations from input list.

            Args:
                input_list (list): List of input tokens.

            Returns:
                list: List of tokens with punctuations removed.
        """

        cleaned_string = self.punctuation_pattern.sub('', ' '.join(input_list))
        return cleaned_string.split()

    def state_updater(self, done: int, process_length: int, section: str, directory: str = ''):
        """
            Updates the state of the preprocessing process.

            Args:
                done (int): Number of processed items.
                process_length (int): Total number of items to be processed.
                section (str): Current preprocessing section.
                directory (str, optional): Directory name being processed. Defaults to ''.
        """

        self.state = [round((done / process_length) * 100, 3), section, directory]

    def preprocess_text(self, input_text: str, normalize: bool = True, tokenize: bool = True,
                        token_spacing: bool = False, remove_stopwords: bool = False, lemmatize: bool = False,
                        stem: bool = False, remove_punctuations: bool = False) -> dict:
        """
            Preprocesses input text based on specified options.

            Args:
                input_text (str): Input text to be preprocessed.
                normalize (bool, optional): Perform normalization. Defaults to True.
                tokenize (bool, optional): Perform tokenization. Defaults to True.
                token_spacing (bool, optional): Perform token spacing. Defaults to False.
                remove_stopwords (bool, optional): Remove stopwords. Defaults to False.
                lemmatize (bool, optional): Perform lemmatization. Defaults to False.
                stem (bool, optional): Perform stemming. Defaults to False.
                remove_punctuations (bool, optional): Remove punctuations. Defaults to False.

            Returns:
                dict: Dictionary containing results of each preprocessing step.
        """

        results = {}
        done = 0
        process_length = len([i for i in [normalize, tokenize, token_spacing, remove_stopwords,
                                          lemmatize, stem, remove_punctuations] if i])

        # Normalize section
        if normalize:
            self.state_updater(done, process_length, "Normalizing...")
            result1 = self.normalize(input_text)
            results['normalize'] = result1
            done += 1
        else:
            result1 = input_text
        sleep(0.3)

        # Tokenize section
        if tokenize:
            self.state_updater(done, process_length, "Tokenizing...")
            result2 = self.tokenize(result1)
            results['tokenize'] = result2
            done += 1
        else:
            result2 = result1.split(" ")
        sleep(0.3)

        # Token Spacing section
        if token_spacing:
            self.state_updater(done, process_length, "Token spacing...")
            result2 = self.token_spacing(result2)
            results['token_spacing'] = result2
            done += 1
        sleep(0.3)

        # Remove stopwords section
        if remove_stopwords:
            self.state_updater(done, process_length, "Remove stopwords...")
            result2 = self.remove_string_stopwords(result2)
            results['remove_stopwords'] = result2
            done += 1
        sleep(0.3)

        # Lemmatize section
        if lemmatize:
            self.state_updater(done, process_length, "Lemmatize...")
            result2 = [self.lemmatize(i) for i in result2]
            results['lemmatize'] = result2
            done += 1

        # Stemming section
        elif stem:
            self.state_updater(done, process_length, "Stemming...")
            result2 = [self.stem(i) for i in result2]
            results['stem'] = result2
            done += 1
        sleep(0.3)

        # Remove Punctuations section
        if remove_punctuations:
            self.state_updater(done, process_length, "Remove punctuations...")
            result2 = self.remove_punctuations(result2)
            results['remove_punctuations'] = result2
            done += 1
        sleep(0.3)

        self.state_updater(done, process_length, "Done!")

        return results

    def internal_preprocess_text(self, input_text: str, normalize: bool = True, tokenize: bool = True,
                                 token_spacing: bool = False, remove_stopwords: bool = False,
                                 lemmatize: bool = False, stem: bool = False, remove_punctuations: bool = False) -> str:
        """
            Preprocesses input text internally based on specified options.

            Args:
                input_text (str): Input text to be preprocessed.
                normalize (bool, optional): Perform normalization. Defaults to True.
                tokenize (bool, optional): Perform tokenization. Defaults to True.
                token_spacing (bool, optional): Perform token spacing. Defaults to False.
                remove_stopwords (bool, optional): Remove stopwords. Defaults to False.
                lemmatize (bool, optional): Perform lemmatization. Defaults to False.
                stem (bool, optional): Perform stemming. Defaults to False.
                remove_punctuations (bool, optional): Remove punctuations. Defaults to False.

            Returns:
                str: Preprocessed text.
        """

        # Normalize section
        if normalize:
            result1 = self.normalize(input_text)
        else:
            result1 = input_text
        sleep(0.3)

        # Tokenize section
        if tokenize:
            result2 = self.tokenize(result1)
        else:
            result2 = result1.split(" ")
        sleep(0.3)

        # Token Spacing section
        if token_spacing:
            result2 = self.token_spacing(result2)
        sleep(0.3)

        # Remove stopwords section
        if remove_stopwords:
            result2 = self.remove_string_stopwords(result2)
        sleep(0.3)

        # Lemmatize section
        if lemmatize:
            result2 = [self.lemmatize(i) for i in result2]

        # Stemming section
        elif stem:
            result2 = [self.stem(i) for i in result2]
        sleep(0.3)

        # Remove Punctuations section
        if remove_punctuations:
            result2 = self.remove_punctuations(result2)
        sleep(0.3)

        return " ".join(result2)

    def preprocess_files(self, input_directory: str, output_directory: str, normalize: bool = True,
                         tokenize: bool = True, token_spacing: bool = False, remove_stopwords: bool = False,
                         lemmatize: bool = False, stem: bool = False, remove_punctuations: bool = False) -> None:
        """
            Preprocesses text files in a directory and writes the preprocessed files to another directory.

            Args:
                input_directory (str): Input directory containing text files.
                output_directory (str): Output directory to write preprocessed files.
                normalize (bool, optional): Perform normalization. Defaults to True.
                tokenize (bool, optional): Perform tokenization. Defaults to True.
                token_spacing (bool, optional): Perform token spacing. Defaults to False.
                remove_stopwords (bool, optional): Remove stopwords. Defaults to False.
                lemmatize (bool, optional): Perform lemmatization. Defaults to False.
                stem (bool, optional): Perform stemming. Defaults to False.
                remove_punctuations (bool, optional): Remove punctuations. Defaults to False.
        """

        directories = os.listdir(input_directory)
        directories_files = {directory: os.listdir(f'{input_directory}/{directory}') for directory in directories}

        done = 0
        process_length = sum([len(files) for directory, files in directories_files.items()])

        for directory, files in directories_files.items():
            for index, file in enumerate(files):
                os.makedirs(os.path.dirname(f'{output_directory}/{directory}/'), exist_ok=True)

                with open(f'{input_directory}/{directory}/{file}', 'r', encoding='utf-8') as f:
                    self.state_updater(done, process_length, f"{file}...", directory)
                    result = self.internal_preprocess_text(
                        "\n".join([i.replace("\n", "").replace('‏', '') for i in f.readlines()]),
                        normalize=normalize, tokenize=tokenize, token_spacing=token_spacing,
                        remove_stopwords=remove_stopwords, lemmatize=lemmatize, stem=stem,
                        remove_punctuations=remove_punctuations)
                    done += 1

                with open(f'{output_directory}/{directory}/{file}', 'w', encoding='utf-8') as f:
                    f.write(result)

        self.state_updater(done, process_length, "Done!")


if __name__ == '__main__':
    text = \
        """
            جودي ابوت، نابغه كاغذي
            سميه نصيري ها
            جودي ابوت را، سال ها است كه مي شناسم، دقيقا از دوران نوجواني. شايد در دوران پرفراز
            و نشيب نوجواني دلم مي خواست جاي او باشم. خيلي از& لحظاتي كه ماجراهايش را مي خواندم 
            دوست داشتم دردسرهاي او مال من باشد. جودي دختري است كه اصولا دردسر درست مي كند و
            اتفاقا دردسرهايش اطرافيان را هم به دردسر مي اندازد. خوب است، قدري باانصاف باشيم. 
            شايد از اين جهت دلم مي خواست جاي جودي باشم كه خداوند در تمام لحظات زندگي يار و ياورش 
            بود. در تمام لحظات سياه و بغرنج زندگي خداوند به ياري اش مي آمد و اوضاع اش سروسامان 
            پيدا مي كرد؟! لطف خداوند هميشه شامل،× حال او بود. 
        """

    P1 = Phase1()
    preprocessed = P1.preprocess_text(text)
    for step, result in preprocessed.items():
        print(step + ':', result)
