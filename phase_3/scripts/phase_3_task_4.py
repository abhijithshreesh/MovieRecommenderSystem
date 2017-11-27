import data_extractor
import config_parser
from util import Util
import config_parser
import data_extractor
from util import Util


class RelevancyFinder(object):

    def __init__(self):
        self.conf = config_parser.ParseConfig()
        self.data_set_loc = self.conf.config_section_mapper("filePath").get("data_set_loc")
        self.data_extractor = data_extractor.DataExtractor(self.data_set_loc)
        self.util = Util()
        self.movie_tag_df = self.util.get_movie_tag_matrix().reset_index()
        #self.movie_tag_df.to_csv(self.data_set_loc + '/movie_tag dataset.csv', index=True, encoding='utf-8')
        #self.relevancy_df = self.fetch_feedback_data()

    def fetch_feedback_data(self):
        data = None
        try:
            data = self.data_extractor.get_task4_feedback_data()
        except:
            print("Feedback file missing.\nAborting...")
            exit(1)

        return data

    def query_point(self, old_query_point, old_query_point_weight):
        self.relevancy_df = self.fetch_feedback_data()
        self.relevancy_df = self.relevancy_df.set_index('moviename')
        merged_data_frame = self.relevancy_df.reset_index().merge(self.movie_tag_df, how="left", on="moviename")
        merged_data_frame = merged_data_frame.set_index('moviename')
        merged_data_frame = merged_data_frame.sort_values('relevancy')
        query_point = merged_data_frame.groupby('relevancy', axis=0).mean()
        query_point.to_csv(self.data_set_loc + '/temp1.csv', index=True, encoding='utf-8')
        query_point = query_point.reset_index()
        gpby = query_point['relevancy']
        #print(type(gpby))
        del query_point['relevancy']
        if query_point.shape[0] == 0:
            query_point = old_query_point * old_query_point_weight
        elif query_point.shape[0] == 1 and gpby.values.__contains__(1):
            query_point = old_query_point * old_query_point_weight + query_point.iloc[0] * (1 - old_query_point_weight)
        elif query_point.shape[0] == 1 and gpby.values.__contains__(0):
            query_point = old_query_point * old_query_point_weight - query_point.iloc[0] * (1 - old_query_point_weight)
        else:
            query_point = old_query_point * old_query_point_weight + (query_point.iloc[1] - query_point.iloc[0]) * (1 - old_query_point_weight)
        #query_point.to_csv(self.data_set_loc + '/temp2.csv', index=True, encoding='utf-8')
        #merged_data_frame.to_csv(self.data_set_loc + '/temp.csv', index=True, encoding='utf-8')
        return query_point

    def relevancy(self, no_r,query_point):
        #movie_names = MovieLSH.query_for_nearest_neighbours(self, query_point, no_r)
        movie_names = self.movie_tag_df['moviename'].sample(n=no_r)
        Util.print_movie_recommendations_and_collect_feedback(self, movie_names, 4, None)


if __name__ == "__main__":
    obj = RelevancyFinder()
    i = True
    j = 2
    qp = obj.query_point(0, 0)
    while i:
        r = int(input("\nEnter value of 'r' : "))
        obj.relevancy(r, qp)
        j += 1
        qp = obj.query_point(qp, 1 - 1/j)
        temp = input('Press any key to continue the search & 0 to stop: ')
        if temp == '0':
            i = False
        else:
            i = True
