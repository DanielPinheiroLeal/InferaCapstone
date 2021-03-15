import gensim as gs
import os as os
import glob
from pathlib import Path

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

from gensim.corpora.textcorpus import TextCorpus
from gensim.test.utils import datapath
from gensim import utils
from gensim.corpora.mmcorpus import MmCorpus
import gensim

from gensim.models import LsiModel

def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text

class Corpus(TextCorpus):

    def get_texts(self):
        files = glob.glob(self.input + "*.txt")
        for file in files:
            file_object = open(file, 'rb')
            file_string = file_object.read()
            words = self.preprocess_text(file_string)
            yield words
    
    def __len__(self):
        self.length = sum(1 for _ in self.get_texts())
        return self.length

class SimilarityModel:
    def __init__(self, corpus_path, model_path, num_latent_dimensions=10):
        self.corpus_path = corpus_path
        self.model_path = model_path
        self.num_latent_dimensions = num_latent_dimensions
        
    def build_corpus(self):
        self.corpus = Corpus(self.corpus_path)
        self.dictionary = self.corpus.dictionary
        MmCorpus.serialize(self.model_path + "corpus", self.corpus)
        self.corpus.dictionary.save(self.model_path + "dictionary")

    def load_corpus(self):
        self.corpus = MmCorpus(self.model_path + "corpus")
        self.dictionary = gensim.corpora.Dictionary.load(self.model_path + "dictionary")

    def train_lsi(self):
        self.lsi_model = LsiModel(self.corpus, num_topics=self.num_latent_dimensions)
        print("Making the LSI:")
        print(self.lsi_model.num_topics)
        self.lsi_model.save(self.model_path + "lsi.model")

    def load_lsi(self):
        self.lsi_model = LsiModel.load(self.model_path + "lsi.model")
        print("Loaded LSI")
        print(self.lsi_model.num_topics)

    def get_lsi_topics(self):
        topics = self.lsi_model.show_topics(-1, formatted=False)

        for topic, words in topics:
            print("Topic {}:".format(topic))
            for word in words:
                print(self.dictionary[int(word[0])])

    def document_map(self):
        pass

    def cluster(self):
        pass

    def save_model(self):
        pass

    def string_lookup(self, input_string):
        pass

def pdf_to_text(input_path, output_path):
    print("Called function")
    files = glob.glob(input_path + "*/*.pdf")

    for file in files:
        print(file)
        file_text = convert_pdf_to_txt(file)
        new_file_name = output_path + Path(file).stem + ".txt"
        text_file = open(new_file_name, 'w')
        text_file.write(file_text)
        text_file.close()
 
if __name__ == '__main__':
    #pdf_to_text("/Users/kamranramji/Documents/NeurIPS/", "/Users/kamranramji/Documents/NeurIPSText/")
    model = SimilarityModel("/Users/kamranramji/Documents/NeurIPSText/", "/Users/kamranramji/Documents/InferaCapstone/model/", 10)
    #model.build_corpus()
    model.load_corpus()
    model.train_lsi()
    model.load_lsi()
    model.get_lsi_topics()


