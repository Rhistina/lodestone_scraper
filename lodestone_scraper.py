#lodestone_scraper
import requests
from bs4 import BeautifulSoup
import re
import datetime
import math


class LodestoneScraper(object):

    def __init__(self):
        self.domain = 'na.finalfantasyxiv.com'
        self.lodestone_url = 'http://{}/lodestone/'.format(self.domain)
        self.session = requests.Session()


    def make_request(self, url=None):
        return self.session.get(url, headers={"User-Agent": "Requests"})


    '''
    Given a character's name and world, return their lodestone id
    '''
    def search_character(self, name, world):
        url = '{}/character/?q={}&worldname={}'.format(self.lodestone_url,name, world)

        r = self.make_request(url)

        soup = BeautifulSoup(r.content, "lxml")

        char_data = soup.select('.entry__link')

        if not char_data:
            return None

        lodestone_id = char_data[0].get('href').split('/')[3]
        return lodestone_id


    '''
    Given a character's name and world, return a dictionary representing character data
    '''
    def get_character(self, name, world):
        lodestone_id = self.search_character(name, world)
        if not lodestone_id:
            return {}

        url = self.lodestone_url + '/character/%s' % lodestone_id
        r = self.make_request(url)

        soup = BeautifulSoup(r.content, "lxml")

        # TO DO calculate average item level
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
        titles = [title.text for title in detail_section.find_all(attrs={'character-block__title'})]
        details = [detail.text for detail in detail_section.find_all(attrs={'character-block__name'})]

        char = {
            'lodestone_id' : lodestone_id,
            'name' : name,
            'jobs' : jobs,
            # TO DO
            # 'avg_item_level' : avg_item_level,
            'current_gear' : equipment,
            'race' : details[0].split('/')[0],
            # TO DO
            # Break apart race and clan
            'clan' : details[0].split('/')[1],
            'gender' : details[0].split('/')[1],
            'nameday' : detail_section.find(attrs={'character-block__birth'}),
            'guardian' : details[1],
            'citystate' : details[2],
            'grandcompany' : details[3].split(" / ")[0],
            'gcrank' : details[3].split(" / ")[1],
            'fc' : detail_section.find(attrs={'character__freecompany__name'}).find('a').text,
            'mounts' : mounts,
            'minions' : minions
            }

        return char


    '''
    Returns a dictionary to represent Free Company data
    '''
    def get_free_company(self, lodestone_id):
        url = '{}/freecompany/{}/'.format(self.lodestone_url,lodestone_id)

        r = self.make_request(url)
        print (url)

        soup = BeautifulSoup(r.content, "lxml")

        # Information from Free Company Top
        fc_name = soup.find(class_='freecompany__text__name').text
        fc_tag = soup.select('p.freecompany__text.freecompany__text__tag')[0].text
        formed =  soup.select('p.freecompany__text script')[0]
        formated_formed_date = datetime.datetime.fromtimestamp(int(re.search(r'ldst_strftime\(([0-9]+),', formed).group(1)))

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

if __name__ == "__main__":
    test = LodestoneScraper()
    result = test.get_free_company(9232238498621208473)
    print(result)


