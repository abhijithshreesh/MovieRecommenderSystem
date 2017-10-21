import logging
from scripts.phase2.common.config_parser import ParseConfig
from scripts.phase2.common.util import Util
import numpy
from sklearn.decomposition import PCA
import logging
import pandas as pd
import operator
from scipy import linalg
from sklearn.preprocessing import StandardScaler
import numpy
from sklearn.decomposition import PCA
from scripts.phase2.common.actor_actor_similarity_matrix import ActorActorMatrix

logging.basicConfig(level=logging.INFO)
from scripts.phase2.task1.phase_2_task_1b_svd import SvdGenreActor

log = logging.getLogger(__name__)
conf = ParseConfig()
util = Util()
actor_actor_matrix_obj = ActorActorMatrix()

class RelatedActorsSvd(SvdGenreActor):
    def __init__(self):
        super().__init__()
        self.data_set_loc = conf.config_section_mapper("filePath").get("data_set_loc")

    def get_related_actors_svd(self, actorid):
        actor_actor_matrix = actor_actor_matrix_obj.fetchActorActorSimilarityMatrix()
        """
        Triggers the compute function and outputs the result tag vector
        :param genre:
        :param model:
        :return: returns a dictionary of Genres to dictionary of tags and weights.
        """

        # Loading the required dataset
        df = pd.DataFrame(pd.read_csv('actor_tag_matrix.csv'))
        df1 = df.values

        # # Feature Scaling
        # sc = StandardScaler()
        # df_sc = sc.fit_transform(df1[:, :])
        #
        # # Calculating SVD
        # U, s, Vh = linalg.svd(df_sc)

        (U, s, Vh) = util.SVD(df1)

        actor_latent_matrix = U[:, :5]

        latent_actor_matrix = actor_latent_matrix.transpose()
        actor_actor_matrix = numpy.dot(actor_latent_matrix, latent_actor_matrix)
        numpy.savetxt("actor_actor_matrix_with_svd_latent_values.csv", actor_actor_matrix, delimiter=",")

        df = pd.DataFrame(pd.read_csv('actor_actor_matrix_with_svd_latent_values.csv', header=None))
        matrix = df.values

        actorids = util.get_sorted_actor_ids()

        index_actor = None
        for i, j in enumerate(actorids):
            if j == actorid:
                index_actor = i
                break

        if index_actor == None:
            print("Actor Id not found.")
            return None

        actor_names = []
        for actor_id in actorids:
            actor_name = util.get_actor_name_for_id(int(actor_id))
            actor_names = actor_names + [actor_name]

        actor_row = matrix[index_actor].tolist()
        actor_actor_dict = dict(zip(actor_names, actor_row))
        del actor_actor_dict[util.get_actor_name_for_id(int(actorid))]

        # for key in actor_actor_dict.keys():
        #     actor_actor_dict[key] = abs(actor_actor_dict[key])

        actor_actor_dict = sorted(actor_actor_dict.items(), key=operator.itemgetter(1), reverse=True)
        return actor_actor_dict

if __name__ == "__main__":
    obj = RelatedActorsSvd()
    actor_actor_dict = obj.get_related_actors_svd(actorid=542238)
    print (actor_actor_dict)
