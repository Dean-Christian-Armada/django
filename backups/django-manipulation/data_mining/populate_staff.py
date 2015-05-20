import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'data_mining.settings')

import django, random, calendar, string
django.setup()

from list.models import Members, Marines, Userlevel
from datetime import date, timedelta


def populate():
	code = ''.join([random.choice(string.uppercase) for n in xrange(4)])
	num = random.randint(0000, 9999)
	firstJan = date.today().replace(day=1, month=1)
	date_issue = firstJan + timedelta(days = random.randint(0, 365 if calendar.isleap(firstJan.year) else 364))
	date_expire = date_issue + timedelta(days=365)

	level = userlevel('seamen')
	member2 = add_member(level, code, 'wally', 'zaide', 'Mr.', 'Wally Zaide', 'PH', 'M', 'Quezon City')
	member1 = add_member(level, code, 'stephen', 'herbert', 'Mr.', 'Stephen Herbert', 'AU', 'M', 'Sydney')
	add_marine(member1, 'Australian Certificate', num, date_issue, date_expire)
	add_marine(member2, 'Philippine Certificate', num, date_issue, date_expire)

	for me in Members.objects.all():
		for ma in Marines.objects.filter(members = me):
			print "- {0} - {1}".format(str(me), str(ma))

def userlevel(userlevel):
	ul = Userlevel.objects.get(userlevel = userlevel)
	return ul

def add_marine(member, cert_name, cert_num, date_issue, date_expire):
	ma = Marines.objects.get_or_create(members=member)[0]
	ma.cert_name = cert_name
	ma.cert_number = cert_num
	ma.date_issue = date_issue
	ma.date_expire = date_expire
	ma.save()
	return ma
def add_member(userlevel, code, username, password, title, name, country, gender, city):
	me = Members.objects.get_or_create(userlevel=userlevel, name=name)[0]
	me.code = code
	me.username = username
	me.password = password
	me.title = title
	me.name = name
	me.country = country
	me.gender = gender
	me.city = city
	me.save()
	return me

if __name__ == '__main__':
	print "Starting Marine population script..."
	populate()