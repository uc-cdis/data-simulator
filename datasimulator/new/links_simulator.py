import copy
from datasimulator.dd_utils import get_parent_label


class EdgeWithLevel():
    def __init__(self, dst, l, level):
        self.dst = dst
        self.link = l
        self.level = level

    def __str__(self):
        self.__repr__()

    def __repr__(self):
        return 'dst: {} - link: {} - level: {}'.format(self.dst, self.link, self.level)

    def __lt__(self, other):
        return self.level < other.level

    def __ge__(self, other):
        return self.level >= other.level


def proportionate_amount(nodes_by_node_name, link_group_by_mask):
    numbers_by_group = {}
    portions = {}
    total = 0
    for k, v in link_group_by_mask.items():
        max_v = 0
        for l in v:
            # if l.link.exclusive_mask > 0:
            if len(nodes_by_node_name[l.dst]) > max_v:
                max_v = len(nodes_by_node_name[l.dst])
        numbers_by_group[k] = max_v
        total += max_v
    for k, v in numbers_by_group.items():
        portions[k] = v/float(total)
    return portions


def get_list_of_links(graph_node, model, exclusive_list):
    name_to_parent = {p.name: p for p in graph_node.parents}
    l_links = []
    for l in exclusive_list:
        n_parent = get_parent_label(model, graph_node.name, l.name)
        if n_parent in name_to_parent:
            l_links.append(EdgeWithLevel(n_parent, l, name_to_parent[n_parent].level))
    return l_links


def group_exlusive_links(exclusive_list, l_links):
    values = list(set(map(lambda x: x.exclusive_mask, exclusive_list)))
    print(l_links)
    print(values)
    link_group_by_mask = {x: [y for y in l_links if y.link.exclusive_mask == x] for x in values}
    link_group_by_mask = {x: y for (x, y) in link_group_by_mask.items() if len(y) > 0}
    if len(link_group_by_mask) > 1 and 0 in link_group_by_mask:
        link_group_by_mask = {x: y.extend(link_group_by_mask[0]) for (x, y) in link_group_by_mask.items() if x != 0}
    link_group_by_mask = {x: sorted(y, reverse=True) for (x, y) in link_group_by_mask.items()}
    return link_group_by_mask


def generate_portion_links(nodes_by_node_name, n_name, start, portion, links):
    data_nodes = nodes_by_node_name[n_name].values()
    end = start + int(portion * len(data_nodes))
    link_names = [l.link.name for l in links]
    print('start: {} - end: {}'.format(start, end))

    js = {}
    for l in links:
        print('Link {}'.format(l.dst))
        js[l.dst] = 0
        nb_dst = len(nodes_by_node_name[l.dst])
        for i in xrange(start, end):
            if (i % 1000 == 0):
                print("   {} / {}".format(i, end))
            if l.link.name not in data_nodes[i]:
                d_node_key = nodes_by_node_name[l.dst].keys()[js[l.dst]]
                data_nodes[i][l.link.name] = {'submitter_id': d_node_key}
                for k in nodes_by_node_name[l.dst][d_node_key].keys():
                    if k in link_names and k not in data_nodes[i]:
                        data_nodes[i][k] = copy.copy(nodes_by_node_name[l.dst][d_node_key][k])
            js[l.dst] = 0 if js[l.dst] == nb_dst-1 else js[l.dst] + 1

    return end


def generate_links(model, nodes_by_node_name, node_name, graph_node, exclusive_list):
    link_group_by_mask = group_exlusive_links(exclusive_list, get_list_of_links(graph_node, model, exclusive_list))
    portions = proportionate_amount(nodes_by_node_name, link_group_by_mask)
    i = 0
    for k, v in link_group_by_mask.items():
        i = generate_portion_links(nodes_by_node_name, node_name, i, portions[k], v)
