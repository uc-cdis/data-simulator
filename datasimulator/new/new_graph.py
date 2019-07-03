from collections import deque


def str_from_list(l):
    s = ""
    for p in l:
        s += p.name + ","
    if len(s) > 0:
        s = s[:-1]
    s = "[{}]".format(s)
    return s


class Node:
    def __init__(self, name, number, parent=None):
        self.name = name
        self.parents = [] if parent is None else [parent]
        self.children = []
        self.level = None
        self.simulated = False
        self.number = number

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "name: {}; number: {}; parents: {}; children: {}; level: {}.".format(
            self.name,
            self.number,
            str_from_list(self.parents),
            str_from_list(self.children),
            self.level,
        )

    def add_child(self, child):
        self.children.append(child)

    def add_parent(self, parent):
        self.parents.append(parent)


class LinkGraph:
    def __init__(self, numbers, dictionary):
        self.dictionary = dictionary
        self.nodes = self.construct_link_tree(numbers)

    def construct_link_tree(self, numbers):
        links = numbers.get("links")
        nodes = {}
        for link in links:
            names = link.split("->")
            if names[1] not in nodes:
                nodes[names[1]] = Node(names[1], int(numbers.get(names[1])))
            if names[0] not in nodes:
                nodes[names[0]] = Node(names[0], int(numbers.get(names[0])))
            nodes[names[0]].add_parent(nodes[names[1]])
            nodes[names[1]].add_child(nodes[names[0]])
        lst_nodes = sorted(self.leverage(nodes.values()), key=lambda k: k.level)
        return lst_nodes

    @staticmethod
    def leverage(nodes):
        root = [n for n in nodes if len(n.parents) == 0][0]
        level = 0
        queue = deque([root])
        while True:
            same_level_queue = deque([])
            while len(queue) > 0:
                cur_node = queue.popleft()
                cur_node.level = level
                for n in cur_node.children:
                    same_level_queue.append(n)
            level += 1
            queue = same_level_queue
            if len(queue) == 0:
                return nodes
