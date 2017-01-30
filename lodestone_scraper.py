#lodestone_scraper
import requests
from bs4 import BeautifulSoup
import re
import datetime


class LodestoneScraper:

    domain = 'na.finalfantasyxiv.com'
    lodestone_url = 'http://%s/lodestone/' % domain
    session = requests.Session()

    def make_request(self, url=None):
        return self.session.get(url)

    '''
    Returns a dictionary to represent Free Company data
    '''
    def get_free_company(self, lodestone_id):
        url = self.lodestone_url + '/freecompany/%s/' % lodestone_id
        r = self.make_request(url)
        soup = BeautifulSoup(r.content, "lxml")

        # Information from Free Company Top
        fc_name = soup.find('span', {'class', 'txt_yellow'}).text
        fc_tag =  soup.select('.vm')[0].contents[-1]
        formed =  soup.select('tr td script')[0].text
        formated_formed_date = str(datetime.datetime.fromtimestamp(int(re.search(r'ldst_strftime\(([0-9]+),', formed).group(1))))

        grand_company = soup.find('div', {'class', 'crest_id centering_h'}).text.split(' ')[0].strip()
        grand_company_standing = soup.find('div', {'class', 'crest_id centering_h'}).text.split(' ')[1].split('\n')[0]
        rank = int(soup.find('tr', {'class', 'rank'}).select('td')[0].text.strip())
        slogan = soup.find(text='Company Slogan').parent.parent.select('td')[0].text

        # TO DO - focus and seeking are not specified for our FC. What does this information look like for other FCs?
        focus = soup.find(text='Focus').parent.parent.select('td')[0].text.strip()
        seeking = soup.find(text='Seeking').parent.parent.select('td')[0].text.strip()
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
        total_member_pages =  soup.find("li", {"class", "next_all"}).find('a').get('href')[-1]


        def get_roster(self, page=1):
            url = self.lodestone_url + '/freecompany/%s/member' % lodestone_id

            r = self.make_request(url + '?page=%s' % page)

            soup = BeautifulSoup(r.content, "lxml")

            member_data = soup.find_all("div", {"class", "player_name_area"})

            for m in member_data:
                member = {
                'name' :  m.contents[1].text.strip().replace('(Gilgamesh)', ''),
                'rank' :  m.contents[3].text.strip(),
                'lodestone_id' : self.lodestone_url + re.sub("/lodestone/", '', m.contents[1].select('a')[0].get('href'))
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

test = LodestoneScraper()
for key, values in (test.get_free_company(9232238498621208473)).items():
    print (key, values)

