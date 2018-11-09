from dictionaryutils import DataDictionary, dictionary

from graph import Graph


def initialize_dictionary(url):
    dictionary.init(DataDictionary(url=url))


def main():
    print("Data simulator software")
    #
    #rl = 'https://s3.amazonaws.com/dictionary-artifacts/datadictionary/develop/schema.json'
    url = 'https://s3.amazonaws.com/dictionary-artifacts/bhcdictionary/0.4.2/schema.json'
    #url = 'https://s3.amazonaws.com/dictionary-artifacts/genomel-dictionary/master/schema.json'
    url = 'https://s3.amazonaws.com/dictionary-artifacts/kf-dictionary/kf-v0.1.2/schema.json'

    url = 'https://s3.amazonaws.com/dictionary-artifacts/datadictionary/develop/schema.json'
    url = 'https://s3.amazonaws.com/dictionary-artifacts/ndhdictionary/3.1.21/schema.json'

    initialize_dictionary(url)

    graph = Graph(dictionary, 'DEV', 'test')

    graph.generate_nodes_from_dictionary()
    graph.construct_graph_edges()

    graph.graph_validation(skip=True)
    
    # orders = []
    # graph.generate_submission_order_whole_graph(orders)
    # print(len(orders))
    # print(len(graph.nodes))
    # for one in orders:
    #    print one.name

    graph.simulate_graph_data()


if __name__ == '__main__':
    main()
