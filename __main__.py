import argparse
from lodestone_scraper import LodestoneScraper
from pprint import pprint

# methods = [method for method in dir(ld) if method.startswith('get') or method.startswith('search')]

ld = LodestoneScraper()


parser = argparse.ArgumentParser()
parser.add_argument('search_for', choices=['fc', 'player'])
parser.add_argument('-n', '--name', help='Name of a player or free company', nargs='+')
parser.add_argument('-s', '--server', help='Server the player or free company resides')
parser.add_argument('-i', '--id', help='Lodestone ID of the player or free company')

args = parser.parse_args()

name = ' '.join(args.name)

if args.search_for=='fc':
    result = ld.get_free_company(name, args.server)

if args.search_for=='player':
    result = ld.get_character(name, args.server)

pprint(result)