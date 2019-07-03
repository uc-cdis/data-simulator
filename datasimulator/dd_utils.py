def get_parent_label(models, node_name, edge_name):
    node = models.Node.get_subclass(node_name)
    edge = getattr(node, edge_name)
    return models.Node.get_subclass_named(edge.target_class.__dst_class__).get_label()


def get_properties(models, node_name):
    node = models.Node.get_subclass(node_name)
    return node.__pg_properties__
