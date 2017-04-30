#!/usr/bin/python3
#   for merlin use shebang: !/usr/local/bin/python3
#	Tomas Kukan
#	Automaticka registrace na SRTGB events
#	aplikace k behu vyzaduje: requests, bs4, xml
#	instalace: python3 -m pip install --user requests bs4 lxml	
#
#	spusteni: ./spartan <regex cas> <regex uroven> <email>
#
import requests
import bs4
import sys
import re
import time
import os

start = time.time() # starttime

def get_token(arg):
	return arg.split("name='csrfmiddlewaretoken' value='")[1].split("'")[0]

def registration_loop():
	print("Spustil se proces registrace s regex: '%s'" %regex)
	s = requests.session()
	while True:
		try:
			r = s.get('http://www.extrabrno.cz/events/')
			if not 'logout/">Odhlásit' in r.text:
				r = s.get('http://www.extrabrno.cz/accounts/login/')
				token = get_token(r.text)
				web = s.post('http://www.extrabrno.cz/accounts/login/',
							 data={ 'login' : 'Kukant96@gmail.com', 'password': 'tadysemdejtotvojeheslo', 'csrfmiddlewaretoken': token})
				r = s.get('http://www.extrabrno.cz/events/')

			tmp = bs4.BeautifulSoup(r.text, "lxml")
			prom = tmp.find('table')
			for line in tmp.find('table').findAll('tr'): # pro kazdy radek v tabulce events
				tds = line.findAll('td')
				if len(tds) == 0:
					continue

				if not re.search(level, tds[2].text): # pokud udalost neodpovida urovni
					continue

				if not re.search(regex, tds[0].text): # pokud udalost neodpovida casu
					continue

				eventid = tds[2].find('a')['href'].split('/')[2]
				r = s.get('http://www.extrabrno.cz/events/%s/' % eventid)
				token = get_token(r.text)
				web = s.post('http://www.extrabrno.cz/events/register-user/?next=/events/%s/' % eventid,
							 data={ 'event-id': eventid, 'csrfmiddlewaretoken': token})
				print(web.text)
				if re.search(r'<button type="submit" class="btn btn-danger">\s*Uvolnit místo\s*</button>', web.text):
					os.system("echo 'Byl jste uspene prihlasen na udalost %s' | mail -s 'registrace-SRTGB' %s" % (regex, email))
					print("Byl jste uspesne prihlasen na udalost %s, konec programu" % tds[0].text)
					exit(0)

		except Exception as er:
			with open("logfile.txt", "a") as logfile:
				print("chyba v logfile: %s\n" % er)
				logfile.write("chyba: %s\n" % er)
		if (time.time() - start) > 604800: # pokud program jede dele jak tyden
			os.system("echo 'Registrace na udalost %s byla neuspena kvuli prekroceni casoveho limitu.' | mail -s 'registrace-SRTGB' %s" % (regex, email))
			print("Ukonceni kvuli prekroceni casu")
			exit(0)
		time.sleep(300) # spi 5 minut, pak zkus znovu
	return

def get_level():
	levels = ["Začátečníci","Pokročilí","Hardcore"]
	for count, level in enumerate(levels):
		print("[%i] " % count + level)
	level = input("Zadejte, prosím, číslo úrovně: ")
	return levels[int(level)]

if __name__ == "__main__":
	print("Login a heslo si upravte ve scriptu na radku cca. 32")
	regex = input("Zadejte prosim datum: ")
	level = get_level()
	email = input("Zadejte prosim email: ")

	registration_loop()
	
