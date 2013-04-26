from re import findall
from entry import Entry


class GedcomFile:
    """
    File class represents a GEDCOM file.
    Attributes are header, trailer, and entries where header and trailer
    are a single entry each and entries is the list of all Entry instances
    parsed in between.
    
    """
    
    def __init__(self, content):
        # TODO: Match file names and import them.
        self.header, self.entries, self.trailer = self.__parse(content)
    
    def __parse(self, lines):
        
        pos = 0
        entries = []
        
        while pos < len(lines):
            pos, entry = self.__process_element(lines, pos)
            if entry.tag == 'HEAD':
                header = entry
            elif entry.tag == 'TRLR':
                trailer = entry
                break
            else:
                entries.append(entry)
    
        return (header, entries, trailer)
    
    __line_reader_regex = (
                        '^(\d{1,2})' +            # Level
                        '(?: (@[A-Z\d]+@))?' +  # Pointer
                        ' _?([A-Z\d]{3,4})' +   # Tag
                        '(?: (.+))?$')            # Value
    
    def __process_element(self, lines, pos):
        parsed_line = findall(self.__line_reader_regex, lines[pos])
        
        if len(parsed_line) != 1:
            raise SyntaxError("Bad GEDCOM syntax in line: '" + lines[pos] + "'")
        
        level, pointer, tag, value = parsed_line[0]
        
        entry = Entry(tag, pointer, value, [])
        
        level = int(level)
        pos += 1
        
        while self.__line_level(lines, pos) > level:
            pos, child_element = self.__process_element(lines, pos)
            entry.children.append(child_element)
        
        return (pos, entry)
    
    def __unicode__(self):
        return (self.header.get_child_value_by_tags('FILE') +
                ' (' +
                self.header.get_child_value_by_tags('DATE') +
                ')')
    
    def __line_level(self, lines, pos):
        return int(lines[pos][:2]) if pos + 1 < len(lines) else 0
    
    def get_entries_by_tag(self, tag):
        return filter(lambda c: c.tag == tag, self.entries)
    
    def get_entry_by_pointer(self, pointer):
        found = filter(lambda e: e.pointer == pointer, self.entries)
        return found[0] if len(found) > 0 else None
