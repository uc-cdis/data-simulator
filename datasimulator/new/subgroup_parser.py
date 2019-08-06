from dictionaryutils import dictionary as gdcdictionary
from collections import deque


class SubgroupParsingNode(object):
    def __init__(self, parent, schema, code=None):
        self.parent = parent
        self.schema = schema
        self.code = code
        self.name = schema.get('name') if 'name' in schema else None
        self.required = schema.get('required', False)
        self.exclusive = schema.get('exclusive', False)
        self.required_links = []
        self.existing_mask = None
        self.existing_links = []
        self.exclusive_mask = 0
        self.exclusive_links = []
        self.all_ancestors_required = parent.all_ancestors_required and parent.required \
            if parent is not None else self.required
        self.all_ancestors_inclusive = parent.all_ancestors_inclusive and not parent.exclusive \
            if parent is not None else not self.exclusive

    def update_existing_mask(self, current, parent, child, update_mask_should_fix):
        parent.existing_mask = current.existing_mask if parent.existing_mask is None \
            else parent.existing_mask | current.existing_mask
        parent.existing_links.append(child.name)
        current.existing_mask = None
        current.existing_links = []
        if not parent.required:
            update_mask_should_fix = False
        return update_mask_should_fix

    def update_exclusive_mask(self, link):
        stack = []
        current = link
        while current.parent and not current.all_ancestors_inclusive:
            parent = current.parent
            if parent.exclusive:
                parent.exclusive_mask |= link.code
                parent.exclusive_links.append(link.name)
            stack.append(current)
            current = parent

        while len(stack) > 0:
            parent = current
            current = stack.pop()
            if parent.exclusive:
                current.exclusive_mask = parent.exclusive_mask ^ current.code
            else:
                current.exclusive_mask = parent.exclusive_mask
            current.exclusive_links = parent.exclusive_links

    def update_parent(self, child):
        update_mask_should_fix = child.required
        self.code = child.code if self.code is None else self.code | child.code
        if update_mask_should_fix:
            self.existing_mask = child.code if self.existing_mask is None else self.existing_mask | child.code
            self.existing_links.append(child.name)

        current_sg = self
        if not current_sg.required:
            update_mask_should_fix = False
        if current_sg.required:
            current_sg.required_links.append(child.name)

        while current_sg is not None:
            parent = current_sg.parent
            if parent is not None:
                if update_mask_should_fix:
                    update_mask_should_fix = self.update_existing_mask(current_sg, parent, child, update_mask_should_fix)
                parent.code = current_sg.code if parent.code is None else parent.code | current_sg.code
                if parent.required:
                    parent.required_links.append(child.name)
            current_sg = parent
        self.update_exclusive_mask(child)

    def add_child_link(self, child):
        self.update_parent(child)


class LinkWithExclusiveMask(object):
    def __init__(self, item):
        self.name = item.name
        self.exclusive_mask = item.exclusive_mask
        self.exclusive_links = item.exclusive_links
        self.multiplicity = item.schema.get('multiplicity')
        self.backref = item.schema.get('backref')

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'EXCLUSIVE: name: {} - exclusive_mask: {} - ' \
               'exclusive_links: {} - backref: {} - multiplicity: {}'.format(
                self.name, self.exclusive_mask, self.exclusive_links,
                self.backref, self.multiplicity)


class ExistingMasks(object):
    def __init__(self, code, existing_mask, existing_links):
        self.code = code
        self.existing_mask = existing_mask
        self.existing_links = existing_links

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'EXISTING: code: {} - existing_mask: {} - ' \
               'existing_links: {}'.format(
                self.code, self.existing_mask, self.existing_links)


class RequiredMask(object):
    def __init__(self):
        self.list_required_links = []
        self.group_required = []
        self.required_mask = 0

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'REQUIRED: required_links: {} - group_required: {} - ' \
               'required_mask: {}'.format(
                self.list_required_links, self.group_required, self.required_mask)


def create_subgroup_validators(dictionary, node_label):
    link_items = []
    leaves = []
    for link in dictionary.schema[node_label]['links']:
        if 'name' in link:
            l_item = SubgroupParsingNode(None, link, 1 << len(leaves))
            leaves.append(l_item)
        else:
            l_item = SubgroupParsingNode(None, link)
        link_items.append(l_item)

    return build_tree_of_link_items(link_items, leaves)


def build_tree_of_link_items(link_items, leaves):
    final_required = []
    current_pos = 0
    while current_pos < len(link_items):
        l_item = link_items[current_pos]
        children_required_count = 0
        if 'subgroup' in l_item.schema:
            for link in l_item.schema['subgroup']:
                if 'subgroup' in link:
                    new_l_item = SubgroupParsingNode(l_item, link)
                else:
                    new_l_item = SubgroupParsingNode(l_item, link, 1 << len(leaves))
                    l_item.add_child_link(new_l_item)
                    leaves.append(new_l_item)

                link_items.append(new_l_item)

                if l_item.required and new_l_item.required:
                    children_required_count += 1
        if l_item.all_ancestors_required and l_item.required and children_required_count == 0:
            final_required.append(l_item)
        current_pos += 1

    required_validator, base_mask = create_required_mask(final_required)
    print required_validator
    existing_list = create_existing_list(link_items, base_mask)
    print existing_list
    exclusive_list = create_exclusive_list(leaves)
    print exclusive_list

    return required_validator, existing_list, exclusive_list


def create_exclusive_list(leaves):
    if len(leaves) == 0:
        return []

    current = leaves[-1]
    leaves_checks = deque([LinkWithExclusiveMask(current)])
    i = len(leaves) - 2
    while i >= 0:
        leaf = leaves[i]
        if leaf.parent == current.parent:
            leaf.exclusive_links = current.exclusive_links
        else:
            current = leaf
        leaves_checks.appendleft(LinkWithExclusiveMask(leaf))
        i -= 1
    return list(leaves_checks)


def create_existing_list(link_items, base_mask):
    return [
        ExistingMasks(item.code, item.existing_mask | base_mask, item.existing_links)
        for item in link_items
        if item.existing_mask is not None
    ]


def create_required_mask(final_required):
    res = RequiredMask()
    base_mask = 0
    for item in final_required:
        res.required_mask |= item.code
        if item.name is not None:
            res.list_required_links.append(item.name)
            base_mask |= item.code  # if the require is True from the root to the leaf, this leaf is really required
        else:
            res.group_required.extend(item.required_links)
    return res, base_mask
