import re
from text_and_vocab.utils import TEXT_DATA_DIR, TAGGED_CORPUS_DIR, BOOK_MAPPING
from os.path import basename
from nltk.tag import str2tuple
from nltk.corpus.reader.tagged import TaggedCorpusReader
from nltk.corpus.reader.util import read_blankline_block
from nltk.corpus.reader import concat, TaggedCorpusView
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


# Customize the TaggedCorpusView to include chapter:verse references at the
# sentence level.
class NTTaggedCorpusView(TaggedCorpusView):

    def __init__(self, corpus_file, encoding, tagged, refs, group_by_sent, sep,
                 word_tokenizer, sent_tokenizer):
        self._refs = refs
        TaggedCorpusView.__init__(self, corpus_file, encoding, tagged,
                                  group_by_sent, False, sep, word_tokenizer,
                                  sent_tokenizer, None, None)

    def read_block(self, stream):
        block = []
        for para_str in read_blankline_block(stream):
            for sent_str in self._sent_tokenizer.tokenize(para_str):
                ref = BOOK_MAPPING.inv[basename(stream.name).replace('.txt',
                                                                     '')] + \
                      ' ' + \
                      self._word_tokenizer.tokenize(sent_str, references=True)
                sent = [str2tuple(s, self._sep)
                        for s in self._word_tokenizer.tokenize(sent_str)]
                if not self._tagged:
                    sent = [w for (w, t) in sent]
                if self._group_by_sent:
                    if self._refs:
                        block.append((ref, sent))
                    else:
                        block.append(sent)
                else:
                    if self._refs:
                        block.extend([(ref, w)
                                      for w in sent])
                    else:
                        block.extend(sent)
        return block


# Customize the TaggedCorpusReader to include a chapter:verse reference for
# each sentence.
class TaggedNTCorpusReader(TaggedCorpusReader):

    def __init__(self, root, fileids):
        TaggedCorpusReader.__init__(self, root, fileids, sep='_')
        self._word_tokenizer = NTWordTokenizer()
        self._sent_tokenizer = RegexpTokenizer('\n', gaps=True)

    def tagged_words(self, fileids=None, refs=False):
        return concat([NTTaggedCorpusView(fileid, enc, True, refs, False,
                                          self._sep, self._word_tokenizer,
                                          self._sent_tokenizer)
                       for (fileid, enc) in self.abspaths(fileids, True)])

    def tagged_sents(self, fileids=None, refs=False):
        return concat([NTTaggedCorpusView(fileid, enc, True, refs, True,
                                          self._sep, self._word_tokenizer,
                                          self._sent_tokenizer)
                       for (fileid, enc) in self.abspaths(fileids, True)])


# Load the text as a TaggedNTCorpusReader.
def load_text_tagged():
    """Load the text as a plaintext NLTK corpus."""
    nt = TaggedNTCorpusReader(TEXT_DATA_DIR + TAGGED_CORPUS_DIR, '.*.txt')
    return nt


if __name__ == '__main__':
    nt = load_text_tagged()
