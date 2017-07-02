import requests
from bs4 import BeautifulSoup
import re
import datetime as dt
import math
import json
import pandas as pd
import logging
from pprint import pprint

gender_map = {'\u2642' : 'Male', '\u2640' : 'Female'}


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LodestoneScraper:

    def __init__(self, debug=False):
        self.domain = 'na.finalfantasyxiv.com'
        self.lodestone_url = 'http://{}/lodestone/'.format(self.domain)
        self.session = requests.Session()
        self.debug = debug

    def make_request(self, url=None):
        return self.session.get(url, headers={"User-Agent": "Requests"})

    def search_character_id(self, name, world) -> str:
        '''
        Given a character's name and world, search for their lodestone id
        '''
        url = '{}/character/?q={}&worldname={}'.format(self.lodestone_url,name, world)

        r = self.make_request(url)

        soup = BeautifulSoup(r.content, "lxml")

        char_data = soup.select('.entry__link')

        if not char_data:
            return

        lodestone_id = char_data[0].get('href').split('/')[3]
        return lodestone_id

    def search_free_company_id(self, name, world) -> str:
        '''
        Given a free company's name and world, search for their lodestone id
        '''
        url = '{}/freecompany/?q={}&worldname={}'.format(self.lodestone_url,name, world)

        r = self.make_request(url)

        soup = BeautifulSoup(r.content, "lxml")

        fc_data = soup.select('.entry__block')

        if not fc_data:
            return

        lodestone_id = fc_data[0].get('href').split('/')[3]
        return lodestone_id

    def get_soup(self, url) -> BeautifulSoup:

        logger.info('get_soup method')

        if self.debug:
            logger.debug("Debug mode ON")
            soup = BeautifulSoup()
        else:
            logger.info("Sending request to {}".format(url))
            r = self.make_request(url)
            if r.ok:
                content = r.json()
                soup = BeautifulSoup(content["content_html"], "html.response")

        return soup

    def get_character(self, name, world) -> dict:
        '''
        Given a character's name and world, return a JSON representing character data
        '''
        lodestone_id = self.search_character_id(name, world)
        if not lodestone_id:
            return json.dumps(['No Data Returned'])

        url = "{}character/{}".format(self.lodestone_url, lodestone_id)
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

        char_data = {
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
        return char_data


    def get_free_company(self, name, world) -> dict :
        '''
        Returns a JSON to represent Free Company data
        '''

        lodestone_id = self.search_free_company_id(name, world)
        if not lodestone_id:
            return json.dumps(['No Data Returned'])

        url = '{}/freecompany/{}/'.format(self.lodestone_url,lodestone_id)

        r = self.make_request(url)

        soup = BeautifulSoup(r.content, "lxml")

        fc_name = soup.find('p', class_='entry__freecompany__name').text
        fc_tag = soup.find('p', class_='freecompany__text__tag').text
        server = soup.find_all('p', class_='entry__freecompany__gc')[1].text.strip()
        grand_company = soup.find('p', class_='entry__freecompany__gc').text.split(' ')
        grand_company_name = grand_company[0]
        grand_company_standing = grand_company[1]
        slogan = soup.find('p', class_='freecompany__text__message').text
        rank = soup.find('h3', text='Rank').find_next().text
        active_numbers = soup.find('h3', text='Active Members').find_next().text
        date_script_contents =  soup.select('p.freecompany__text script')[0].text
        extracted_unix_time = re.search(r'ldst_strftime\(([0-9]+),', date_script_contents).group(1)

        try :
            formated_formed_date = dt.datetime.fromtimestamp(int(extracted_unix_time)).strftime('%Y-%m-%d')
        except ValueError:
            logger.debug('Unable to parse formed date')
            formated_formed_date = None

        # focus = []
        # for element in soup.find(text='Focus').parent.parent.select('td')[0].find_all('li'):
        #     try:
        #         foo = element['class']
        #     except KeyError:
        #         focus.append(element.img['title'])
        #
        # if not focus:
        #     focus = "None Specified"
        #
        # seeking = []
        # for element in soup.find(text='Seeking').parent.parent.select('td')[0].find_all('li'):
        #     try:
        #         foo = element['class']
        #     except KeyError:
        #         seeking.append(element.img['title'])
        #
        # if not seeking:
        #     seeking = "None Specified"

        # Make a dictionary comprehension?
        fc_standings = {}
        fc_standings_info = soup.find('table', class_='character__ranking__data').select('th')
        for ele in fc_standings_info:
            arr = ele.text.split(":")
            key = arr[0]
            value = arr[1].split(" ")[0]
            fc_standings[key] = value

        active = soup.find('h3', text='Active').find_next().text.strip()

        estate = {}
        estate['name'] =  soup.find('p', class_='freecompany__estate__name').text
        estate['address'] = soup.find('p', text='Address').find_next().text
        estate['greeting'] = soup.find('p', text='Greeting').find_next().text

        # Information from Free Company > Members
        roster = []

        # Make initial soup to figure out max number of Member pages for this Free Company
        url = '{}/freecompany/{}/member/'.format(self.lodestone_url, lodestone_id)
        r = self.make_request(url)
        soup = BeautifulSoup(r.content, "lxml")
        total_member_pages = int(soup.find(class_='btn__pager__current').text.split(' ')[-1])

        def get_roster(self, page=1):
            url = '{}/freecompany/{}/member'.format(self.lodestone_url, lodestone_id)

            r = self.make_request('{}?page={}'.format(url, page))

            soup = BeautifulSoup(r.content, "lxml")

            member_data = soup.find_all('li', class_='entry')

            for m in member_data:
                member_lodestone = member_data[0].find('a').get('href')

                member = {
                # This is hardcoded to Gilgamesh. Will probably have to split on '(' and take the first element
                'name' :  m.find(class_='entry__name').text,
                'rank' :  m.find('span').text,
                'lodestone_id': member_data[0].find('a').get('href').split('/')[-2],
                'lodestone_url' : 'http://{}{}'.format(self.domain, member_lodestone)
                }
                roster.append(member)

        # For every member page, populate the Free Company roster
        for page in range(1, int(total_member_pages)+1):
            get_roster(self, page)

        free_company_data = {
            'fc_name' : fc_name,
            'fc_tag' : fc_tag,
            'server' : server,
            'formed' : formated_formed_date,
            'active_members' : active_numbers,
            'roster' : roster,
            'gc' : grand_company_name,
            'gc_standing' : grand_company_standing,
            'rank' : rank,
            'slogan' : slogan,
            # 'focus' : focus,
            # 'seeking' : seeking,
            'fc_standing' : fc_standings,
            'active' : active,
            'estate' : estate
        }
        return free_company_data

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
    test = LodestoneScraper(False)
    logger.warning(pd.Timestamp.now())
    ## Almost 2 seconds to scrape character information
    # result = test.get_character('Oren Iishi', 'Gilgamesh')
    ## Almost 10 seconds to scrape free company information
    result = test.get_free_company('Ascended', 'Gilgamesh')

    # Almost 6 seconds to simply request the main FC page, member once, and the 5 member pages
    # requests.get('http://na.finalfantasyxiv.com/lodestone/freecompany/9232238498621208473/')
    # requests.get('http://na.finalfantasyxiv.com/lodestone/freecompany/9232238498621208473/member/')
    # requests.get('http://na.finalfantasyxiv.com/lodestone/freecompany/9232238498621208473/member/')
    # requests.get('http://na.finalfantasyxiv.com/lodestone/freecompany/9232238498621208473/member/?page=2')
    # requests.get('http://na.finalfantasyxiv.com/lodestone/freecompany/9232238498621208473/member/?page=3')
    # requests.get('http://na.finalfantasyxiv.com/lodestone/freecompany/9232238498621208473/member/?page=4')
    # requests.get('http://na.finalfantasyxiv.com/lodestone/freecompany/9232238498621208473/member/?page=5')

    logger.warning(pd.Timestamp.now())

