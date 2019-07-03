from collections import deque


class Node():
    def __init__(self, name, parent=None):
        self.name = name
        self.parents = [] if parent is None else [parent]
        self.children = []
        self.level = None
        self.simulated = False

    def add_child(self, child):
        self.children.append(child)

    def add_parent(self, parent):
        self.parents.append(parent)


class LinkGraph():
    def __init__(self, mapping):
        self.mapping = mapping
        self.nodes = self.construct_link_tree(mapping)

    def construct_link_tree(self, mapping):
        links = mapping.get('links')
        nodes = {}
        for link in links:
            names = link.split('->')
            if names[0] not in nodes:
                nodes[names[0]] = Node(names[0], names[1])
            if names[1] not in nodes:
                nodes[names[1]] = Node(names[1])
            nodes[names[0]].add_parent(nodes[names[1]])
            nodes[names[1]].add_child(nodes[names[0]])
        lst_nodes = sorted(self.leverage(nodes.values()), key=lambda k: k.level, reverse=True)
        return lst_nodes

    def leverage(self, nodes):
        root = [n for n in nodes if len(n.parents) == 0][0]
        level = 0
        queue = deque([root])
        while True:
            same_level_queue = deque([])
            while(len(queue) > 0):
                cur_node = queue.popleft()
                cur_node.level = level
                for n in cur_node.children:
                    same_level_queue.append(n)
            level += 1
            if (len(same_level_queue) == 0):
                return nodes

    def simulate_tree(self):
        for n in self.nodes:
            self.simulate_node(n)

    def simulate_node(self, node):
        pass
