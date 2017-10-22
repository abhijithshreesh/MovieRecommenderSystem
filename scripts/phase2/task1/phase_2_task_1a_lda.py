import pandas as pd
import logging
from scripts.phase2.common.config_parser import ParseConfig
from scripts.phase2.common.task_2 import GenreTag
from sklearn.preprocessing import Imputer
from sklearn.decomposition import LatentDirichletAllocation
import argparse
from collections import Counter
from gensim import corpora, models
import gensim

logging.basicConfig(level=logging.INFO)

log = logging.getLogger(__name__)
conf = ParseConfig()

class LdaGenreTag(GenreTag):
    def __init__(self):
        super().__init__()
        self.data_set_loc = conf.config_section_mapper("filePath").get("data_set_loc")


    def get_tag_count(self, tag_series):
        counter = Counter()
        for each in tag_series:
            counter[each] += 1
        return dict(counter)

    def get_lda_data(self, genre):
        data_frame = self.get_genre_data().reset_index()
        genre_data_frame = data_frame[data_frame["genre"]==genre]
        tag_df = genre_data_frame.groupby(['movieid'])['tag'].apply(list).reset_index()
        tag_df = tag_df.sort_values('movieid')
        #tag_df.to_csv('movie_tag_lda.csv', index=True, encoding='utf-8')
        #movieid_list = tag_df.movieid.tolist()
        #tag_matrix = tag_df[["tag"]].values
        #tag_matrix = list(tag_matrix.iloc[:,1])
        tag_df = list(tag_df.iloc[:,1])

        # turn our tokenized documents into a id <-> term dictionary
        dictionary = corpora.Dictionary(tag_df)

        # convert tokenized documents into a document-term matrix
        corpus = [dictionary.doc2bow(text) for text in tag_df]

        # generate LDA model
        lda = gensim.models.ldamodel.LdaModel(corpus, num_topics=5, id2word=dictionary, passes=1)

        latent_semantics = lda.print_topics(5,80)
        for latent in latent_semantics:
            print (latent)

        #print (lda.print_topics(5,80))

        corpus = lda[corpus]

        for i in corpus:
            print(i)



        #lda = LatentDirichletAllocation(n_topics=4)

        #lda.fit_transform(genre_tag_freq.values)
        #topics = lda.components_

        #ldamodel = gensim.models.ldamodel.LdaModel(tag_df.values, num_topics=3)
        #print(ldamodel.print_topics(num_topics=3, num_words=3))

        # Loading the dataset
        #df = pd.DataFrame(pd.read_csv('tag_df_lda.csv'))
        #df1 = df.values
        #print(df1)

        # Encoding the String Variables

        # from sklearn.preprocessing import LabelEncoder
        # labelencoder_df = LabelEncoder()
        # df.iloc[:, 1] = labelencoder_df.fit_transform(df.iloc[:, 1])
        # df.iloc[:, 2] = labelencoder_df.fit_transform(df.iloc[:, 2])
        #
        # df1 = df.values

        # Calling the LDA algorithm


if __name__ == "__main__":
    obj = LdaGenreTag()
    lda_comp = obj.get_lda_data(genre="Action")
    print (lda_comp)