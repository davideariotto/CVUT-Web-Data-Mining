import csv


CLUSTERING_EXCLUDE_TOPICS = set(['Neni', 'Nezjisten', 'Obecne'])
SOFT_C = 'n_sleva.asp', 'jak_se_prihlasit.htm', 'n_pojistenick.asp', 'n_kdojsme.asp'
HARD_C = 'n_prihlaska.asp', 'n_katalog.asp'


def read_csv(filename, delimiter=','):
    return csv.DictReader(open(filename, 'rb'), delimiter=delimiter)


def process_visitors(item):
    id = item.pop('VisitID')
    item.update(ref_map[item.pop('Referrer')])
    return id, item


def process_clicks(item):
    item.update(visitors.get(item['VisitID'], {}))
    page = item.get('PageName', '')
    item['soft_c'] = any(map(page.endswith, SOFT_C))
    item['hard_c'] = any(map(page.endswith, HARD_C))
    return item


def export(data, filename='results.csv', fieldnames=None):
    fieldnames = fieldnames or data[0].keys()
    writer = csv.DictWriter(open(filename, 'w+'), fieldnames, restval='0')
    # write header
    writer.writerow(dict(zip(fieldnames, fieldnames)))
    writer.writerows(data)


def export_clustering(data):
    def get_topic(item):
        topic = item['TopicName']
        return topic
        # zkraceni, aby se to veslo do plot view v RapidMineru:
        #return '%s%s' % (topic[:10], topic[-2:].upper() if len(topic) > 12 else '')
    c_data = {}
    for item in data:
        topic = get_topic(item)
        if topic in CLUSTERING_EXCLUDE_TOPICS: continue
        visitor_entry = c_data.setdefault(item['VisitID'], {})
        visitor_entry.setdefault(topic, 0)
        visitor_entry[topic] += 1
    topics = sorted(set(map(get_topic, data)) - CLUSTERING_EXCLUDE_TOPICS)
    export(c_data.values(), 'clustering.csv', topics)


def export_assoc(data):
    data_by_visitor = {}
    for item in data:
        data_by_visitor.setdefault(item['VisitID'], []).append(item)

    def time(x):
        h = int(x)
        if h < 6 or h > 22: return 'noc'
        if h < 10: return 'rano'
        if h < 13: return 'dopoledne'
        if h < 18: return 'odpoledne'
        if h < 23: return 'vecer'

    def avg_time(items):
        s = sum([int(i['TimeOnPage']) for i in items]) / len(items)
        if s < 60: return 'kratce'
        if s <= 150: return 'stredne'
        return 'dlouho'

    def process(items):
        first = items[0]
        return {
            'MekkaKonverze': any([i.get('soft_c') for i in items]),
            'TvrdaKonverze': any([i.get('hard_c') for i in items]),
            'Den': ('vikend' if first['Den'] in ('Saturday', 'Sunday') else
                    'vsedni'),
            'Cas': time(first['Hodina']),
            'TypOdkazovace': first['TypOdkazovace'],
            'LandingPage': first['PageName'],
            'LandingTopicName': first['TopicName'],
            'LandingCategory': first['ExtCatName'],
            'PocetStranek': 'malo' if len(items) < 8 else 'hodne',
            'AvgTimeOnPage': avg_time(items),
        }
    assoc_data = map(process, data_by_visitor.values())
    export(assoc_data, 'assoc.csv')


def filter_rules(filename='assoc-rules.txt',
                 output_filename='filtered-assoc-rules.txt'):
    open(output_filename, 'w+').writelines(
        filter(lambda r: 'Konverze' in r.split('==>')[1], open(filename, 'rb'))
    )


ref_map = dict([(i['Referrer'], i) for i in read_csv('search_engine_map.csv')])
visitors = dict(map(process_visitors, read_csv('visitors.csv', ';')))
everything = filter(lambda item: int(item.get('Delka_pocetstranek', 0)) > 2,
                    map(process_clicks, read_csv('clicks.csv')))


if __name__ == '__main__':
    export_clustering(everything)
    export_assoc(everything)
