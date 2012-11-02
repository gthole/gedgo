class Entry:
	"""Entry class represents a single entry in a GEDCOM File object.
	An entry has a tag.  It may optionally have a pointer (typically represented
	as '@I\d+@') or a value.  The entry also may contain a list of sub-entries,
	stored here as children, that are all the entries on a higher level.
	
	"""
	def __init__(self, tag, pointer, value, children):
		self.tag = tag
		self.pointer = pointer.strip('@')
		self.value = value
		self.children = children
	
	def get_child_value_by_tags(self, tags, default=None):
		entry = self
		if type(tags) is str:
			tags = [tags]
		for tag in tags:
			no_matching_tag = True
			for child in entry.children:
				if child.tag == tag:
					no_matching_tag = False
					entry = child
					break
			if no_matching_tag:
				break
		if no_matching_tag:
			return default
		value = entry.value
		for child in entry.get_children_by_tag('CONC'):
			value += child.value
		return value
	
	def get_child_by_tag(self, tag):
		children = self.get_children_by_tag(tag)
		if len(children) > 0:
			return children[0]
		else:
			return None
	
	def get_children_by_tag(self, tag):
		return filter(lambda c : c.tag == tag, self.children)