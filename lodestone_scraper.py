import requests
from bs4 import BeautifulSoup
import re
import datetime
import math
import json
import pandas as pd
from logging import getLogger
from pprint import pprint

gender_map = {'\u2642' : 'Male', '\u2640' : 'Female'}

json_test = {
    "citystate": "Ul'dah",
    "clan": " \u2640",
    "current_gear": [
        [
            "Augmented Shire Custodian's Circlet",
            "Item Level 270",
            "Head"
        ],
        [
            "Augmented Shire Custodian's Earrings",
            "Item Level 270",
            "Earrings"
        ],
        [
            "Alexandrian Neckband of Fending",
            "Item Level 270",
            "Necklace"
        ],
        [
            "Alexandrian Sollerets of Fending",
            "Item Level 270",
            "Feet"
        ],
        [
            "Augmented Shire Custodian's Ring",
            "Item Level 270",
            "Ring"
        ],
        [
            "Alexandrian Belt of Fending",
            "Item Level 270",
            "Waist"
        ],
        [
            "Alexandrian Gauntlets of Fending",
            "Item Level 270",
            "Hands"
        ],
        [
            "Alexandrian Ring of Fending",
            "Item Level 270",
            "Ring"
        ],
        [
            "Soul of the Dark Knight",
            "Item Level 30",
            "Soul Crystal"
        ],
        [
            "Augmented Shire Custodian's Bracelet",
            "Item Level 270",
            "Bracelets"
        ],
        [
            "Augmented Shire Greatsword",
            "Item Level 270",
            "Dark Knight's Arm"
        ],
        [
            "Alexandrian Mail of Fending",
            "Item Level 270",
            "Body"
        ],
        [
            "Alexandrian Breeches of Fending",
            "Item Level 270",
            "Legs"
        ]
    ],
    "fc": "Ascended",
    "gcrank": "Second Storm Lieutenant",
    "gender": " \u2640",
    "grandcompany": "Maelstrom",
    "guardian": "Nald'thal, the Traders",
    "jobs": [
        [
            "Paladin",
            "60",
            "0 / 4470000"
        ],
        [
            "Warrior",
            "60",
            "0 / 4470000"
        ],
        [
            "Dark Knight",
            "60",
            "0 / 4470000"
        ],
        [
            "Pugilist",
            "15",
            "3586 / 30500"
        ],
        [
            "Dragoon",
            "60",
            "0 / 4470000"
        ],
        [
            "Rogue",
            "-",
            "- / -"
        ],
        [
            "Samurai",
            "-",
            "- / -"
        ],
        [
            "White Mage",
            "60",
            "0 / 4470000"
        ],
        [
            "Scholar",
            "60",
            "0 / 4470000"
        ],
        [
            "Astrologian",
            "54",
            "557158 / 1872000"
        ],
        [
            "Bard",
            "60",
            "0 / 4470000"
        ],
        [
            "Machinist",
            "-",
            "- / -"
        ],
        [
            "Thaumaturge",
            "30",
            "134305 / 162500"
        ],
        [
            "Summoner",
            "60",
            "0 / 4470000"
        ],
        [
            "Red Mage",
            "-",
            "- / -"
        ],
        [
            "Carpenter",
            "50",
            "0 / 864000"
        ],
        [
            "Blacksmith",
            "50",
            "136538 / 864000"
        ],
        [
            "Armorer",
            "50",
            "51191 / 864000"
        ],
        [
            "Goldsmith",
            "50",
            "68060 / 864000"
        ],
        [
            "Leatherworker",
            "50",
            "11524 / 864000"
        ],
        [
            "Weaver",
            "50",
            "11829 / 864000"
        ],
        [
            "Alchemist",
            "50",
            "500 / 864000"
        ],
        [
            "Culinarian",
            "50",
            "0 / 864000"
        ],
        [
            "Miner",
            "50",
            "23942 / 864000"
        ],
        [
            "Botanist",
            "59",
            "16265 / 3888000"
        ],
        [
            "Fisher",
            "-",
            "- / -"
        ]
    ],
    "lodestone_id": "2023059",
    "minions": [
        "Storm Hatchling",
        "Black Chocobo Chick",
        "Princely Hatchling",
        "Chocobo Chick Courier",
        "Midgardsormr",
        "Baby Behemoth",
        "Morbol Seedling",
        "Baby Bun",
        "Chigoe Larva",
        "Wide-eyed Fawn",
        "Baby Raptor",
        "Wolf Pup",
        "Coeurl Kitten",
        "Tiny Tortoise",
        "Dust Bunny",
        "Pudgy Puk",
        "Buffalo Calf",
        "Cactuar Cutting",
        "Smallshell",
        "Infant Imp",
        "Beady Eye",
        "Fledgling Dodo",
        "Coblyn Larva",
        "Goobbue Sproutling",
        "Bite-sized Pudding",
        "Demon Brick",
        "Slime Puddle",
        "Kidragora",
        "Onion Prince",
        "Eggplant Knight",
        "Garlic Jester",
        "Tomato King",
        "Mandragora Queen",
        "Pumpkin Butler",
        "Minute Mindflayer",
        "Tight-beaked Parrot",
        "Wind-up Brickman",
        "Baby Opo-opo",
        "Naughty Nanka",
        "Mummy's Little Mummy",
        "Demon Box",
        "Unicolt",
        "Owlet",
        "Ugly Duckling",
        "Lesser Panda",
        "Page 63",
        "Accompaniment Node",
        "Korpokkur Kid",
        "Morpho",
        "Poro Roggo",
        "Fenrir Pup",
        "Mammet #003L",
        "Cait Sith Doll",
        "Wind-up Moogle",
        "Wind-up Goblin",
        "Wind-up Cursor",
        "Wind-up Airship",
        "Minion Of Light",
        "Wind-up Leader",
        "Wind-up Odin",
        "Wind-up Gilgamesh",
        "Wind-up Ultros",
        "Toy Alexander",
        "Nana Bear",
        "Wind-up Warrior Of Light",
        "Wind-up Firion",
        "Wind-up Kain",
        "Wind-up Shantotto",
        "Magic Broom",
        "Gold Rush Minecart",
        "Wind-up Leviathan",
        "Wind-up Ramuh",
        "Wind-up Shiva",
        "Wind-up Minfilia",
        "Wind-up Thancred",
        "Dress-up Thancred",
        "Wind-up Moenbryda",
        "Wind-up Alphinaud",
        "Wind-up Cid",
        "Wind-up Nanamo",
        "Wind-up Louisoix",
        "Wind-up Haurchefant",
        "Wind-up Aymeric",
        "Wind-up Edda"
    ],
    "mounts": [
        "Company Chocobo",
        "Ceremony Chocobo",
        "Black Chocobo",
        "Fat Chocobo",
        "Magitek Armor",
        "Gilded Magitek Armor",
        "Coeurl",
        "War Panther",
        "Ahriman",
        "Behemoth",
        "Warlion",
        "Griffin",
        "Zu",
        "Manacutter",
        "Gobwalker",
        "Witch's Broom",
        "Arrhidaeus",
        "Unicorn",
        "Nightmare",
        "Aithon",
        "Xanthos",
        "Gullfaxi",
        "Markab",
        "Boreas",
        "Rose Lanner",
        "Midgardsormr"
    ],
    "name": "Oren Iishi",
    "nameday": "25th Sun of the 6th Umbral Moon",
    "race": "Miqo'teSeeker of the Sun ",
    "titles": [
        "Race/Clan/Gender",
        "Nameday",
        "Guardian",
        "City-state",
        "Grand Company"
    ]
}

class LodestoneScraper:

    def __init__(self, debug=False):
        self.domain = 'na.finalfantasyxiv.com'
        self.lodestone_url = 'http://{}/lodestone/'.format(self.domain)
        self.session = requests.Session()
        self.debug = debug

    def make_request(self, url=None):
        return self.session.get(url, headers={"User-Agent": "Requests"})

    def search_character(self, name, world):
        '''
        Given a character's name and world, return their lodestone id
        '''
        url = '{}/character/?q={}&worldname={}'.format(self.lodestone_url,name, world)

        r = self.make_request(url)

        soup = BeautifulSoup(r.content, "lxml")

        char_data = soup.select('.entry__link')

        if not char_data:
            return None

        lodestone_id = char_data[0].get('href').split('/')[3]
        return lodestone_id

    def get_soup(self, url):

        logger = getLogger(__name__)
        logger.info('get_soup method')
        if self.debug:
            logger.debug("Debug mode ON")
            soup = json_test
        else:
            logger.info("Sending request to {}".format(url))
            r = self.make_request(url)
            if r.ok:
                content = r.json()
                soup = BeautifulSoup(content["content_html"], "lxml")

        return soup

    def get_character(self, name, world):
        '''
        Given a character's name and world, return a JSON representing character data
        '''
        lodestone_id = self.search_character(name, world)
        if not lodestone_id:
            return json.dumps(['No Data Returned'])

        url = self.lodestone_url + '/character/%s' % lodestone_id
        r = self.make_request(url)
        soup = BeautifulSoup(r.content, "lxml")

        # Remove br tags cus they suck
        for br in soup.find_all('br'):
            br.replace_with('/')

        item_names = [item.text for item in soup.find_all(class_='db-tooltip__item__name')]
        item_levels = [ilvl.text for ilvl in soup.find_all(class_='db-tooltip__item__level')]
        item_categories = [category.text for category in soup.find_all(class_='db-tooltip__item__category')]
        equipment = [item for item in set(zip(item_names,item_levels,item_categories))]

        job_names = [name.text for name in soup.find_all('div', class_='character__job__name')]
        job_levels = [level.text for level in soup.find_all('div', class_='character__job__level')]
        job_exps = [exp.text for exp in soup.find_all('div', class_='character__job__exp')]
        jobs = [job for job in zip(job_names, job_levels, job_exps)]

        mount_section = soup.find('div', class_='character__mounts')
        mounts = mount_section.find_all(attrs={'data-tooltip':True})
        mounts = [mount['data-tooltip'] for mount in mounts]

        minion_section = soup.find('div', class_='character__minion')
        minions = minion_section.find_all(attrs={'data-tooltip':True})
        minions = [minion['data-tooltip'] for minion in minions]

        detail_section = soup.find('div', class_='character__profile__data__detail')
        # titles = [title.text for title in detail_section.find_all(attrs={'character-block__title'})]
        details = [detail.text for detail in detail_section.find_all(attrs={'character-block__name'})]

        char = {
            'lodestone_id' : lodestone_id,
            'name' : name,
            'jobs' : jobs,
            'avg_item_level' : self.calculate_average_item_level(equipment),
            'current_gear' : equipment,
            'race' : details[0].split('/')[0],
            'clan' : details[0].split('/')[1],
            'gender' : gender_map.get(details[0].split('/')[2].strip()),
            'nameday' : detail_section.find(attrs={'character-block__birth'}).text,
            'guardian' : details[1],
            'citystate' : details[2],
            'grandcompany' : details[3].split(" / ")[0],
            'gcrank' : details[3].split(" / ")[1],
            'fc' : detail_section.find(attrs={'character__freecompany__name'}).find('a').text,
            'mounts' : mounts,
            'minions' : minions
            }

        result = json.dumps(char, indent=4, sort_keys=True)

        return result


    def get_free_company(self, lodestone_id) -> json :
        '''
        Returns a JSON to represent Free Company data
        '''
        url = '{}/freecompany/{}/'.format(self.lodestone_url,lodestone_id)

        r = self.make_request(url)

        soup = BeautifulSoup(r.content, "lxml")

        # Information from Free Company Top
        fc_name = soup.find(class_='freecompany__text__name').text
        fc_tag = soup.select('p.freecompany__text.freecompany__text__tag')[0].text
        formed =  soup.select('p.freecompany__text script')[0]
        formated_formed_date = 'test' #datetime.datetime.fromtimestamp(int(re.search(r'ldst_strftime\(([0-9]+),', formed).group(1)))

        grand_company = soup.find('div', {'class', 'crest_id centering_h'}).text.split(' ')[0].strip()
        grand_company_standing = soup.find('div', {'class', 'crest_id centering_h'}).text.split(' ')[1].split('\n')[0]
        rank = int(soup.find('tr', {'class', 'rank'}).select('td')[0].text.strip())
        slogan = soup.find(text='Company Slogan').parent.parent.select('td')[0].text

        focus = []
        for element in soup.find(text='Focus').parent.parent.select('td')[0].find_all('li'):
            try:
                foo = element['class']
            except KeyError:
                focus.append(element.img['title'])

        if not focus:
            focus = "None Specified"
                
        seeking = []
        for element in soup.find(text='Seeking').parent.parent.select('td')[0].find_all('li'):
            try:
                foo = element['class']
            except KeyError:
                seeking.append(element.img['title'])

        if not seeking:
            seeking = "None Specified"        

        active = soup.find(text='Active').parent.parent.select('td')[0].text.strip()

        estate = {}
        estate_profile = soup.find(text='Estate Profile').parent.parent
        estate['name'] =  estate_profile.select('.txt_yellow')[0].text
        estate['address'] = estate_profile.select('p.mb10')[0].text
        estate['greeting'] = estate_profile.select('p.mb10')[1].text

        # Information from Free Company > Members
        roster = []

        # Make initial soup to figure out max number of Member pages for this Free Company
        url = self.lodestone_url + '/freecompany/%s/member' % lodestone_id
        r = self.make_request(url)
        soup = BeautifulSoup(r.content, "lxml")
        total_member_pages =  soup.find("span", {"class", "total"}).text
        total_member_pages =  math.ceil(int(total_member_pages)/50)


        def get_roster(self, page=1):
            url = self.lodestone_url + '/freecompany/%s/member' % lodestone_id

            r = self.make_request('{}?page={}'.format(url,page))

            soup = BeautifulSoup(r.content, "lxml")

            member_data = soup.find_all("div", {"class", "player_name_area"})

            for m in member_data:
                member = {
                # This is hardcoded to Gilgamesh. Will probably have to split on '(' and take the first element
                'name' :  m.contents[1].text.partition("(")[0].strip(),
                'rank' :  m.contents[3].text.strip(),
                'lodestone_id': m.contents[1].select('a')[0].get('href').split('/')[3],
                'lodestone_url' : self.lodestone_url + re.sub("/lodestone/", '', m.contents[1].select('a')[0].get('href'))
                }
                roster.append(member)

        # For every member page, populate the Free Company roster
        for i in range(1, int(total_member_pages)+1):
            get_roster(self,i)

        return {
            'fc_name' : fc_name,
            'fc_tag' : fc_tag,
            'formed' : formated_formed_date,
            'active_members' : len(roster),
            'roster' : roster,
            'gc' : grand_company,
            'gc_standing' : grand_company_standing,
            'rank' : rank,
            'slogan' : slogan,
            'focus' : focus,
            'seeking' : seeking,
            'active' : active,
            'estate' : estate
        }

    def calculate_average_item_level(self, equipement) -> float:
        '''
            Given a list of equipment, calculate the average item level
        '''
        category_to_exclude = ['Soul Crystal']

        gear_df = pd.DataFrame(equipement, columns=['name', 'level', 'category'])
        gear_df.level =  gear_df.level.str.split(' ').str.get(2).astype(int)

        gear_to_exclude = gear_df.category.isin(category_to_exclude)
        gear_df = gear_df.loc[~gear_to_exclude].reset_index()

        return gear_df.level.mean()

if __name__ == "__main__":
    test = LodestoneScraper(True)
    result = test.get_character('Oren Iishi', 'Gilgamesh')
    print(result)
