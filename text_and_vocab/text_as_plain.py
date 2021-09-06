import re
from file_locations import TEXT_DATA_DIR, PLAIN_CORPUS_DIR, BOOK_MAPPING
from os.path import basename
from nltk.corpus import PlaintextCorpusReader
from nltk.corpus.reader import concat
from nltk.tokenize.api import TokenizerI
from nltk.tokenize.regexp import RegexpTokenizer


# Custom sentence tokenizer that excludes the chapter:verse reference at the
# beginning of each line.
class NTWordTokenizer(TokenizerI):
    def tokenize(self, text, references=False):
        if not references:
            return [tok for tok in re.compile(' ').split(text) if tok][1:]
        else:
            return re.sub(' .*', '', text)


# Customize the PlaintextCorpusReader to include a chapter:verse reference for
# each sentence.
class PlainNTCorpusReader(PlaintextCorpusReader):

    def __init__(self, root, fileids):
        PlaintextCorpusReader.__init__(self, root, fileids)
        self._word_tokenizer = NTWordTokenizer()
        self._sent_tokenizer = RegexpTokenizer('\n', gaps=True)

    def _read_ref_sent_block(self, stream):
        ref_sents = []
        for para in self._para_block_reader(stream):
            ref_sents.extend([(BOOK_MAPPING.inv[basename(stream.name).replace('.txt', '')] +
                               ' ' +
                               self._word_tokenizer.tokenize(ref_sent, references=True),
                               self._word_tokenizer.tokenize(ref_sent))
                              for ref_sent in self._sent_tokenizer.tokenize(para)])
        return ref_sents

    def _read_ref_block(self, stream):
        return [ref_sent[0] for ref_sent in self._read_ref_sent_block(stream)]

    def _read_sent_block(self, stream):
        return [ref_sent[1] for ref_sent in self._read_ref_sent_block(stream)]

    def refs(self, fileids=None):
        return concat(
            [self.CorpusView(path, self._read_ref_block, encoding=enc)
             for (path, enc, fileid) in self.abspaths(fileids, True, True)]
        )


# Load the text as a PlainNTCorpusReader.
def load_text_plain():
    """Load the text as a plaintext NLTK corpus."""
    nt = PlainNTCorpusReader(TEXT_DATA_DIR + PLAIN_CORPUS_DIR, '.*.txt')
    return nt


if __name__ == '__main__':
    nt = load_text_plain()
