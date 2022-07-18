import requests, re, json
from bs4 import BeautifulSoup as bs4


def scrape_github(search_term, num_pages=1):
	'''Scrapes the github repos from the given search term

	Parameters
	----------
	search_term : str
			The search term for the github repositories
	num_pages : int
			The number of pages to scrape

	Returns
	-------
	scraped_info : list
			A list of dictionaries containing the necessary information from the scraped repos

	'''
	search_term = search_term.replace(' ', '+')

	URL = 'https://github.com/search?q='+search_term
	page = requests.get(URL)

	soup = bs4(page.content, 'html.parser')
	division = soup.find_all('div', class_='mt-n1')
	search_items = []
	for division_i in division:

		division_i_section_2 = division_i.select('div')[1].select('div')[1]

		repo_name = division_i.find('div', class_='f4 text-normal').a.get_text()
		repo_descrip = division_i.p.get_text().strip()
		
		num_stars = division_i_section_2.find('svg').parent
		if num_stars != None:
			num_stars = num_stars.get_text(strip=True)
		
		tags = []
		for tag in division_i.select('div')[1].div.find_all(class_="topic-tag"):
			tags.append(tag.get_text(strip=True))

		language = division_i.find(itemprop='programmingLanguage')
		if language != None:
			language = language.get_text(strip=True)

		license = division_i.find_all(text=re.compile('license'), limit=1)
		if len(license) > 0:
			license = license[0].strip()
		else:
		 	license = None

		last_update = division_i.find('relative-time')
		if last_update:
			if last_update.has_attr('datetime'):
				last_update = last_update['datetime']

		num_issues = division_i_section_2.find_all(text=re.compile('issue'), limit=1)
		if len(num_issues) > 0:
			num_issues = int(re.search(r'\d+', num_issues[0]).group())
			# Getting the int num issues
		else:
			num_issues = None
		
		search_item = {
			"repo_name":repo_name,
			"description":repo_descrip,
			"tags":tags,
			"num_stars":num_stars,
			"language":language,
			"license":license,
			"last_update":last_update,
			"num_issues":num_issues
		}
		search_items.append(search_item)

	formatted_string = json.dumps(search_items, indent=4)
	formatted_string = formatted_string.replace("null", "None").replace(': "None"', ': None')
	formatted_string = formatted_string.replace('"repo_name"', 'repo_name').replace('"description"', 'description')
	formatted_string = formatted_string.replace('"tags"', 'tags').replace('"num_stars"', 'num_stars').replace('"language"', 'language')
	formatted_string = formatted_string.replace('"license":', 'license:').replace('"last_update"', 'last_update').replace('"num_issues"', 'num_issues')
	
	pattern = re.compile('tags: \[(\n            ".*(\s)*.*",?)*\n        \]')

	matches = pattern.finditer(formatted_string)

	for match in matches:
		new_match = match[0].replace('\n        ]', ']')
		new_match = new_match.replace('\n            ', ' ')
		new_match = new_match.replace('"', "'")
		formatted_string = formatted_string.replace(match[0], new_match)

	return formatted_string


def github_api(search_term, num_pages=1):
	'''Searches for repositories with the given search term using the GitHub REST API

	Parameters
	----------
	search_term : str
			The search term for the github repositories
	num_pages : int
			The number of pages required to query for repositories

	Returns
	-------
	repo_info : list
			A list of dictionaries containing the necessary info from the repositories
	'''
	items = []
	search_term = search_term.replace(' ', '+')

	URL = 'https://api.github.com/search/repositories?q='+search_term+"&per_page=10&page=1"
	page = requests.get(URL)
	data = json.loads(page.text)

	for item in data.get("items"):

		license = "None"
		if item:
			if item.get("license"):
				if item.get("license").get("name") != "Other":
					license = item.get('license').get("name")

		search_item = {
			"repo_name":item.get("full_name"),
			"description":item.get("description"),
			"num_stars":item.get("stargazers_count"),
			"language":item.get("language"),
			"license":license,
			"last_update":item.get("updated_at"),
			"has_issues":item.get("has_issues")
		}
		items.append(search_item)

	formatted_string = json.dumps(items, indent=4)
	formatted_string = formatted_string.replace("null", "None")
	formatted_string = formatted_string.replace('"repo_name"', 'repo_name').replace('"description"', 'description')
	formatted_string = formatted_string.replace('"tags"', 'tags').replace('"num_stars"', 'num_stars').replace('"language"', 'language')
	formatted_string = formatted_string.replace('"license":', 'license:').replace('"last_update"', 'last_update').replace('"num_issues"', 'num_issues')
	formatted_string = formatted_string.replace('"has_issues":', 'has_issues:').replace('"None"', 'None')
	return formatted_string

