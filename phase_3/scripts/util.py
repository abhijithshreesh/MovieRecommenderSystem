import logging
import math
import operator
import os

import gensim
import numpy
import pandas as pd
import tensorly.tensorly.decomposition as decomp
from config_parser import ParseConfig
from data_extractor import DataExtractor
from gensim import corpora
from scipy import linalg

logging.getLogger("gensim").setLevel(logging.CRITICAL)


class Util(object):
    """
    Class containing all the common utilities used across the entire code base
    """
    def __init__(self):
        self.conf = ParseConfig()
        self.data_set_loc = os.path.join(os.path.abspath(os.path.dirname(__file__)), self.conf.config_section_mapper("filePath").get("data_set_loc"))
        self.data_extractor = DataExtractor(self.data_set_loc)
        self.mlratings = self.data_extractor.get_mlratings_data()
        self.mlmovies = self.data_extractor.get_mlmovies_data()
        self.imdb_actor_info = self.data_extractor.get_imdb_actor_info_data()
        self.genome_tags = self.data_extractor.get_genome_tags_data()

    def get_sorted_actor_ids(self):
        """
        Obtain sorted actor ids
        :return: list of sorted actor ids
        """
        actor_info = self.data_extractor.get_imdb_actor_info_data()
        actorids = actor_info.id
        actorids = actorids.sort_values()
        return actorids

    def get_movie_id(self, movie):
        """
        Obtain name ID for the name passed as input
        :param movie:
        :return: movie id
        """
        all_movie_data = self.mlmovies
        movie_data = all_movie_data[all_movie_data['moviename'] == movie]
        movie_id = movie_data['movieid'].unique()

        return movie_id[0]

    def get_average_ratings_for_movie(self, movie_id):
        """
        Obtain average rating for movie
        :param movie_id:
        :return: average movie rating
        """
        all_ratings = self.mlratings
        movie_ratings = all_ratings[all_ratings['movieid'] == movie_id]

        ratings_sum = 0
        ratings_count = 0
        for index, row in movie_ratings.iterrows():
            ratings_count += 1
            ratings_sum += row['rating']

        return ratings_sum / float(ratings_count)

    def get_actor_name_for_id(self, actor_id):
        """
        actor name for id
        :param actor_id:
        :return: actor name for the actor id
        """
        actor_data = self.imdb_actor_info[self.imdb_actor_info['id'] == actor_id]
        name = actor_data['name'].unique()

        return name[0]

    def get_movie_name_for_id(self, movieid):
        """
        movie name for movie id
        :param movieid:
        :return: movie name
        """
        all_movie_data = self.mlmovies
        movie_data = all_movie_data[all_movie_data['movieid'] == movieid]
        movie_name = movie_data['moviename'].unique()

        return movie_name[0]

    def get_tag_name_for_id(self, tag_id):
        """
        tag name for tag id
        :param tag_id:
        :return: tag name
        """
        tag_data = self.genome_tags[self.genome_tags['tagId'] == tag_id]
        name = tag_data['tag'].unique()

        return name[0]

    def partition_factor_matrix(self, matrix, no_of_partitions, entity_names):
        """
        Function to partition the factor matrix into groups as per 2-norm distance
        :param matrix:
        :param no_of_partitions:
        :param entity_names:
        :return: dictionary containing the groups
        """
        entity_dict = {}
        for i in range(0, len(matrix)):
            length = 0
            for latent_semantic in matrix[i]:
                length += abs(latent_semantic) ** 2
            entity_dict[entity_names[i]] = math.sqrt(length)

        max_length = float(max(entity_dict.values()))
        min_length = float(min(entity_dict.values()))
        length_of_group = (float(max_length) - float(min_length)) / float(no_of_partitions)

        groups = {}
        for i in range(0, no_of_partitions):
            groups["Group " + str(i + 1) + " ( " + str(min_length + float(i * length_of_group)) + " , " + str(
                min_length + float((i + 1) * length_of_group)) + " )"] = []

        for key in entity_dict.keys():
            entity_length = entity_dict[key]
            group_no = math.ceil(float(entity_length - min_length) / float(length_of_group))
            if group_no == 0:
                group_no = 1
            groups["Group " + str(group_no) + " ( " + str(
                min_length + float((group_no - 1) * length_of_group)) + " , " + str(
                min_length + float(group_no * length_of_group)) + " )"].append(key)

        return groups

    def get_latent_semantics(self, r, matrix):
        """
        Function to obtain the latent semantics for the factor matrix
        :param r:
        :param matrix:
        :return: top 'r' latent semantics
        """
        latent_semantics = []
        for latent_semantic in matrix:
            if len(latent_semantics) == r:
                break
            latent_semantics.append(latent_semantic)

        return latent_semantics

    def print_partitioned_entities(self, groupings):
        """
        Pretty print groupings
        :param groupings:
        """
        for key in groupings.keys():
            print(key)
            if len(groupings[key]) == 0:
                print("NO ELEMENTS IN THIS GROUP\n")
                continue
            for entity in groupings[key]:
                print(entity, end="|")
            print("\n")

    def print_latent_semantics(self, latent_semantics, entity_names_list):
        """
        Pretty print latent semantics
        :param latent_semantics:
        :param entity_names_list:
        """
        for latent_semantic in latent_semantics:
            print("Latent Semantic:")
            dict1 = {}
            for i in range(0, len(entity_names_list)):
                dict1[entity_names_list[i]] = float(latent_semantic[i])
            for s in sorted(dict1, key=dict1.get, reverse=True):  # value-based sorting
                print(str(s) + "*(" + str(dict1[s]) + ")", end="")
                print(" + ", end="")
            print("\n")

    def CPDecomposition(self, tensor, rank):
        """
        Perform CP Decomposition
        :param tensor:
        :param rank:
        :return: factor matrices obtained after decomposition
        """
        factors = decomp.parafac(tensor, rank)
        return factors

    def SVD(self, matrix):
        """
        Perform SVD
        :param matrix:
        :return: factor matrices and the core matrix
        """
        U, s, Vh = linalg.svd(matrix, full_matrices=False)
        return (U, s, Vh)

    def PCA(self, matrix):
        """
        Perform PCA
        :param matrix:
        :return: factor matrices and the core matrix
        """
        cov_df = numpy.cov(matrix, rowvar=False)
        U, s, Vh = linalg.svd(cov_df)

        return (U, s, Vh)

    def LDA(self, input_compound_list, num_topics, num_features):
        """
        Perform LDA
        :param input_compound_list:
        :param num_topics:
        :param num_features:
        :return: topics and object topic distribution
        """
        dictionary = corpora.Dictionary(input_compound_list)
        corpus = [dictionary.doc2bow(text) for text in input_compound_list]
        lda = gensim.models.ldamodel.LdaModel(corpus, num_topics, id2word=dictionary, passes=20)
        latent_semantics = lda.print_topics(num_topics, num_features)
        corpus = lda[corpus]

        return corpus, latent_semantics

    def get_doc_topic_matrix(self, u, num_docs, num_topics):
        """
        Reconstructing data
        :param u:
        :param num_docs:
        :param num_topics:
        :return: reconstructed data
        """
        u_matrix = numpy.zeros(shape=(num_docs, num_topics))

        for i in range(0, len(u)):
            row1 = u[i]
            for j in range(0, len(row1)):
                u_matrix[i, j] = row1[j][1]

        return u_matrix

    def get_transition_dataframe(self, data_frame):
        """
        Function to get the transition matrix for Random walk
        :param data_frame:
        :return: transition matrix
        """
        for column in data_frame:
            data_frame[column] = pd.Series(
                [0 if ind == int(column) else each for ind, each in zip(data_frame.index, data_frame[column])],
                index=data_frame.index)
        data_frame["row_sum"] = data_frame.sum(axis=1)
        for column in data_frame:
            data_frame[column] = pd.Series(
                [each / sum if (column != "row_sum" and each > 0 and ind != int(column) and sum!=0) else each for ind, each, sum in
                 zip(data_frame.index, data_frame[column], data_frame.row_sum)],
                index=data_frame.index)
        data_frame = data_frame.drop(["row_sum"], axis=1)
        data_frame.loc[(data_frame.T == 0).all()] = float(1 / (len(data_frame.columns)))
        data_frame = data_frame.transpose()
        return data_frame

    def get_seed_matrix(self, transition_df, seed_nodes, nodes):
        """
        Function to get the Restart matrix for entries in the seed list
        :param transition_df:
        :param seed_nodes:
        :param nodeids:
        :return: seed_matrix
        """
        seed_matrix = [0.0 for each in range(len(transition_df.columns))]
        seed_value = float(1 / len(seed_nodes))
        seed_value_list = [seed_value for seed in seed_nodes]
        delta = seed_value / len(seed_nodes)
        for i in range(0, len(seed_nodes) - 1):
            seed_value_list[i] = seed_value_list[i] + (len(seed_nodes) - 1 - i) * delta
            for j in range(i + 1, len(seed_nodes)):
                seed_value_list[j] = seed_value_list[j] - delta
        for each in seed_nodes:
            seed_matrix[list(nodes).index(each)] = seed_value_list[list(seed_nodes).index(each)]
        return seed_matrix

    def print_nodes_and_pageranks(self, page_rank_tuple):
        for first, second in page_rank_tuple:
            print("%s[%s]: %s" % (first, self.get_movie_id(first), second))

    def compute_pagerank(self, seed_nodes, node_matrix, nodes):
        """
        Function to compute the Personalised Pagerank for the given input
        :param seed_actors:
        :param actor_matrix:
        :param actorids:
        :return:
        """
        data_frame = pd.DataFrame(node_matrix)
        transition_df = self.get_transition_dataframe(data_frame)
        seed_matrix = self.get_seed_matrix(transition_df, seed_nodes, nodes)
        result_list = seed_matrix
        temp_list = []
        while(temp_list!=result_list):
            temp_list = result_list
            result_list = list(0.85*numpy.matmul(numpy.array(transition_df.values), numpy.array(result_list))+ 0.15*numpy.array(seed_matrix))
        page_rank_dict = {i: j for i, j in zip(nodes, result_list)}
        sorted_rank = sorted(page_rank_dict.items(), key=operator.itemgetter(1), reverse=True)
        self.print_nodes_and_pageranks(sorted_rank[0:len(seed_nodes)+5])
        return sorted_rank[0:len(seed_nodes)+5]


if __name__ == "__main__":
    obj = Util()
    actorids = obj.get_sorted_actor_ids()
    print("Actorids Sorted along with original index: \n")
    print(actorids)