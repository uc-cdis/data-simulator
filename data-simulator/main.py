from dictionaryutils import DataDictionary, dictionary

from node import Graph


def initialize_dictionary(url):
    dictionary.init(DataDictionary(url=url))


def main():
    print("Data simulator software")
    #
    #rl = 'https://s3.amazonaws.com/dictionary-artifacts/datadictionary/develop/schema.json'
    url = 'https://s3.amazonaws.com/dictionary-artifacts/bhcdictionary/0.4.2/schema.json'
    #url = 'https://s3.amazonaws.com/dictionary-artifacts/genomel-dictionary/master/schema.json'

    initialize_dictionary(url)

    graph = Graph(dictionary, 'DEV', 'test')

    graph.generate_nodes_from_dictionary()
    graph.generate_full_graph()
    orders = graph.gen_submission_order()
    print(len(orders))
    print(len(graph.nodes))
    #for one in orders:
    #    print one.name

    graph.test_simulatation()


if __name__ == '__main__':
    main()
