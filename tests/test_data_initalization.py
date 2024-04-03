from datasimulator.main import initialize_graph
import argparse

def test_data_validation():
    url = "https://s3.amazonaws.com/dictionary-artifacts/bhcdictionary/0.4.3/schema.json"
    args = {}
    # parser = argparse.ArgumentParser()
    # parser.add_argument("url", default=url, help=f"Description of {url}")
    # args = parser.parse_args()
    graph = initialize_graph(
        dictionary_url=url,
        program=args.program if hasattr(args, "program") else None,
        project=args.project if hasattr(args, "project") else None,
        consent_codes=args.consent_codes if hasattr(args, "consent_codes") else None)
    result = graph.graph_validation()
    assert False
