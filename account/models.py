import re
import random
import datetime
import sha

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User, UserManager

# Create your models here.

SHA1_RE = re.compile('^[a-f0-9]{40}$')
PHONE_TYPE = (	('home', 'Home'),
				('work', 'Work'),
				('cell', 'Cell'),
				('other', 'Other'),
			)

class CustomUser(User):	
	bio = models.TextField()
	
	objects = UserManager()
	def __unicode__(self):
		return self.username
		
	class Meta(object):
		verbose_name = "Muckraker"

	def save(self):
		password = ""
		r = re.compile('sha1\$.*')
		if not r.match(self.password):
			password = self.password
			self.set_password(self.password)
		User.save(self)
		
class RegistrationManager(models.Manager):
	def create_new_user(self, username, password, email):
		if not self.activation_expired():
			new_user = CustomUser.objects.create_user(username, email, password)
			new_user.is_active = False
			
			profile = self.create_profile(new_user)
			
			current_site = Site.objects.get_current()
			subject = 'Please activate'
			subject = ''.join(subject.splitlines())
			message = render_to_string('account/activation_email.txt', {
				'activation_key': profile.activation_key,
				'expire': settings.ACCOUNT_ACTIVATION_DAYS,
				'site': current_site
				})
			send_email(subject, message, 'donotreply@%s' % current_site, [ new_user.email ])
			
	def create_profile(self, user):

		salt = sha.new(str(random.random())).hexdigest()[:5]
		activation_key = sha.new(salt+user.username).hexdigest()
		return self.create(user=user,
                           activation_key=activation_key)

	def activation_key_expired(self):

		expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
		return self.activation_key == "ALREADY_ACTIVATED" or \
               (self.user.date_joined + expiration_date <= datetime.datetime.now())
	activation_key_expired.boolean = True

	def delete_expired_users(self):
		for profile in self.all():
			if profile.activation_key_expired():
				user = profile.user
				if not user.is_active:
					user.delete()

class RegistrationProfile(models.Model):
	userid = models.ForeignKey(CustomUser)
	activation_key = models.CharField(max_length=40)
	objects = RegistrationManager()



class PhoneBook(models.Model):
	userid = models.ForeignKey(CustomUser, blank=True, null=True)
	phone_type = models.CharField(max_length=20, choices=PHONE_TYPE, blank=False, default='Home')
	phone_number = models.CharField(max_length=30)

class AddressBook(models.Model):
	userid = models.ForeignKey(CustomUser, blank=True, null=True)
	address = models.CharField(max_length=50)
	city = models.CharField(max_length=50)
	state = models.CharField(max_length=30)
	zipcode = models.CharField(max_length=20)
	country = models.CharField(max_length=50)




















from django.contrib.auth import models as auth_models
from django.contrib.auth.management import create_superuser
from django.db.models import signals

# From http://stackoverflow.com/questions/1466827/ --
#
# Prevent interactive question about wanting a superuser created.  (This code
# has to go in this otherwise empty "models" module so that it gets processed by
# the "syncdb" command during database creation.)
signals.post_syncdb.disconnect(
	create_superuser,
	sender=auth_models,
	dispatch_uid='django.contrib.auth.management.create_superuser')


# Create our own test user automatically.

def create_testuser(app, created_models, verbosity, **kwargs):
	if not settings.DEBUG:
		return
	try:
		auth_models.User.objects.get(username='chief')
	except auth_models.User.DoesNotExist:
		print '*' * 80
		print 'Creating test user -- login: chief, password: kwlee123'
		print '*' * 80
		user = CustomUser(username='chief', email='x@x.com', password='kwlee123')
		print '*' * 80
		print 'Making chief the superuser'
		user.is_staff = True
		user.is_superuser = True
		print '*' * 80
		user.save()
	else:
		print 'Chief already exists.'

signals.post_syncdb.connect(create_testuser,
    sender=auth_models, dispatch_uid='common.models.create_testuser')