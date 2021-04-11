import gensim as gs
import os as os
import glob
from pathlib import Path

from tika import parser

from gensim.corpora.textcorpus import TextCorpus
from gensim.test.utils import datapath
from gensim import utils
from gensim.corpora.mmcorpus import MmCorpus
import gensim

from gensim.parsing.preprocessing import preprocess_string

from gensim.models import LsiModel, LdaModel, LogEntropyModel

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
    def __init__(self, corpus_path, model_path, num_latent_dimensions=10, num_topics=10):
        self.corpus_path = corpus_path
        self.model_path = model_path
        self.num_latent_dimensions = num_latent_dimensions
        self.num_topics = num_topics

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
        self.lsi_model.save(self.model_path + "lsi.model")

    def load_lsi(self):
        self.lsi_model = LsiModel.load(self.model_path + "lsi.model")
    
    def train_log_entropy(self):
        self.LogEntropyModel = LogEntropyModel(self.corpus)
        self.LogEntropyModel.save(self.model_path + "logentropy.model")
    
    def load_log_entropy(self):
        self.LogEntropyModel = LogEntropyModel.load(self.model_path + "logentropy.model")

    def get_lsi_topics(self):
        topics = self.lsi_model.show_topics(-1, formatted=False)

        for topic, words in topics:
            print("Topic {}:".format(topic))
            for word in words:
                print(self.dictionary[int(word[0])])

    def document_map(self, filename):
        '''

        Maps input filname to lsi model co-ordinates and LDA topics

        '''
        file = Path(self.corpus_path + filename + ".txt")
        if file.exists():
            file = open(self.corpus_path + filename + ".txt", 'rb')
            string = file.read()
        else:
            print("Document map is using an empty string")
            string = ""
        
        words = preprocess_string(string)
        bow = self.dictionary.doc2bow(words)
        return self.lsi_model[bow], self.lda_model[bow]

    def train_lda_model(self):
        self.lda_model = LdaModel(self.corpus, self.num_topics, self.dictionary)
        self.lda_model.save(self.model_path + "lda.model")

    def load_lda_model(self):
        self.lda_model = LdaModel.load(self.model_path + "lda.model")

    def get_lda_topic_terms(self):
        topics = self.lda_model.show_topics(formatted=False)
        for topic in topics:
            print("Next topic: ")
            for term in topic[1]:
                print(term[0])

    def string_lookup(self, input_string):
        '''
        String-to-lsi lookup
        '''
        words = preprocess_string(input_string)
        bow = self.dictionary.doc2bow(words)
        return self.lsi_model[bow]

def pdf_to_text(input_path, output_path):
    files = glob.glob(input_path + "*/*.pdf")

    for file in files:
        print(file)
        parsed_pdf = parser.from_file(file)
        file_text = parsed_pdf['content']
        if file_text is None: file_text = ""
        new_file_name = output_path + Path(file).stem + ".txt"
        text_file = open(new_file_name, 'w', encoding='utf-8')
        text_file.write(file_text)
        text_file.close()

if __name__ == '__main__':
    pdf_to_text(r"/Users/kamranramji/Documents/NeurIPS", r"/Users/kamranramji/Documents/InferaCapstone/NeurIPSText")

    model = SimilarityModel(r"/Users/kamranramji/Documents/InferaCapstone/NeurIPSText/", r"/Users/kamranramji/Documents/InferaCapstone/model/", 10)
    model.build_corpus()
    #model.load_corpus()
    model.train_lsi()
    model.train_lda_model()
    model.train_log_entropy()

    #model.load_lsi()
    #model.load_lda_model()
    # print("LSI AXES now printing")
    # model.get_lsi_topics()
    # print("LDA TOPICS now printing")
    # model.get_lda_topic_terms()
    # print("Calling document map")
    # print(model.document_map("Instance-based_Generalization_in_Reinforcement_Learning"))
    # print("Calling string lookup")
    # print(model.string_lookup("Reinforcement learning"))


