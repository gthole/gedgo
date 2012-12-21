from datetime import datetime

import random
import json


def json_tree(person):
	n = node(person, 0)
	return json.dumps(n)


def node(person, level):
	r = {}
	r['name'] = truncate(person.full_name())
	r['span'] = '(' + person.year_range() + ')'
	r['id'] = person.pointer
	if (level < 2) and person.child_family:
		r['children'] = []
		if person.child_family.husbands.all():
			for parent in person.child_family.husbands.all():
				r['children'].append(node(parent, level + 1))
		if person.child_family.wives.all():
			for parent in person.child_family.wives.all():
				r['children'].append(node(parent, level + 1))
		while len(r['children']) < 2:
			if person.child_family.husbands.all():
				r['children'].append({'name': 'unknown', 'span': ''})
			else:
				r['children'].prepend({'name': 'unknown', 'span': ''})
	return r


def truncate(inp):
	return (inp[:25] + '..') if len(inp) > 27 else inp


def timeline(person):
	personal = []
	now = datetime.now().year

	if not valid_event_date(person.birth):
		return ([], 0)
	if (not valid_event_date(person.death)) & (now - person.birth.date.year > 100):
		return ([], 0)

	personal.append(['born', person.birth.date.year])

	if person.spousal_families.all():
		for family in person.spousal_families.all():
			if valid_event_date(family.marriage):
				personal.append(["married", family.marriage.date.year])
			if valid_event_date(family.divorce):
				personal.append(["divorced", family.divorce.date.year])
			for child in family.children.all():
				if valid_event_date(child.birth):
					personal.append([child.full_name() + " born", child.birth.date.year])
				if valid_event_date(child.death):
					if child.death.date.year < person.birth.date.year:
						personal.append([child.full_name() + " died", child.death.date.year])

	if not valid_event_date(person.death):
		personal.append(["now", now])
	else:
		personal.append(["died", person.death.date.year])

	lifespan = (personal[-1][1] - personal[0][1])

	gathered = __gatherby(personal, lambda e: e[1])
	personal = []
	for events in gathered:
		if len(events) == 1:
			personal.append(events[0])
		else:
			name = []
			for event in events:
				name.append(event[0])
			personal.append([', '.join(name), events[0][1]])

	dates = map(lambda x: x[1], personal)
	dates = dates + map(lambda x: x + 1, dates) + map(lambda x: x - 1, dates)
	historical = filter(lambda x: (x[1] not in dates) & (x[1] > dates[0]) & (x[1] < dates[-1]), HISTORICAL)
	number = max((lifespan / 6) + 2 - len(personal), 5)
	historical = random.sample(historical, min([len(historical), number]))  # TODO: auto fill in by heuristic

	if len(personal) < 3:
		return ([], 0)

	return (historical + personal, len(historical))


def valid_event_date(event):
	if event != None:
		if event.date != None:
			return True
	return False


def __gatherby(inlist, func, equivalencefunc=lambda a, b: a == b):
	"__gatherby(list, func) returns a list of lists of items in list which have equal values of func(item)."
	keys = []
	gathered = []
	for item in inlist:
		key = func(item)
		index = -1
		for i in range(0, len(keys)):
			if equivalencefunc(key, keys[i]):
				index = i
				break
		if index == -1:
			keys.append(key)
			gathered.append([])
		gathered[index].append(item)
	return gathered

# TODO: Switch to database storage?
HISTORICAL = [
	['First Nobel Prizes awarded', 1901],
	['NYC subway opens', 1904],
	['Einstein proposes Theory of Relativity', 1905],
	['Picasso introduces Cubism', 1907],
	['Plastic invented', 1909],
	['Chinese Revolution', 1911],
	['Ford assembly line opens', 1913],
	['Panama Canal opens', 1914],
	['Battles of Somme, Verdun', 1916],
	['WWI ends', 1919],
	["Women's suffrage succeeds in US", 1920],
	['Tomb of King Tut discovered', 1922],
	['Roaring twenties in full swing', 1925],
	['Lindbergh flies solo over Atlantic', 1927],
	['Penicillin discovered', 1928],
	['US stock market crashes', 1929],
	['Pluto discovered', 1930],
	['Air conditioning invented', 1932],
	['US Prohibition ends', 1933],
	['The Dust Bowl', 1934],
	['US Social Security begun', 1935],
	['Spanish Civil War begins', 1936],
	['Hindenberg disaster', 1937],
	['WWII Begins', 1939],
	['Manhattan Project begins', 1941],
	['Stalingrad / Midway', 1942],
	['D-Day', 1944],
	['First computer built', 1945],
	['Sound barrier broken', 1947],
	['Big Bang theory established', 1948],
	['NATO established', 1949],
	['First Peanuts cartoon strip', 1950],
	['Color TV introduced', 1951],
	['Queen Elizabeth coronated', 1952],
	['DNA discovered', 1953],
	['Segregation ruled illegal', 1954],
	['Warsaw pact', 1955],
	['Sputnik launched', 1957],
	['First TV presidential debate', 1960],
	['Cuban missile crisis', 1962],
	['I Have a Dream speech', 1963],
	['US sends troops to Vietnam', 1965],
	['Summer of love', 1967],
	['Beatles release Let It Be', 1969],
	['VCRs introduced', 1971],
	['M*A*S*H premiers', 1972],
	['Watergate scandal hits', 1973],
	['Microsoft founded', 1975],
	['Steve Jobs invents Apple I', 1976],
	['Star Wars released', 1977],
	['John Paul II becomes Pope', 1978],
	['First space station launched', 1979],
	['John Lennon dies', 1980],
	['Space shuttle first orbital flight', 1981],
	['Sally Ride is first woman in space', 1983],
	['Wreck of the Titanic discovered', 1985],
	['Chernobyl disaster', 1986],
	['Berlin wall falls', 1989],
	['World Wide Web is invented', 1990],
	['Nelson Mandela elected', 1994],
	['South Africa repeals apartheid law', 1991],
	['Hong Kong transferred to China', 1997],
	['The Euro is introduced', 1999],
	['Wikipedia founded', 2001],
	['Human genome project completed', 2003],
	['Barack Obama sworn US President', 2009],
	['population reaches 7 billion', 2011]
]
