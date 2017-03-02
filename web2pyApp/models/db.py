# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.14.1":
    raise HTTP(500, "Requires web2py 2.13.3 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
request.requires_https()

# -------------------------------------------------------------------------
# app configuration made easy. Look inside private/appconfig.ini
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
myconf = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(myconf.get('db.uri'),
             pool_size=myconf.get('db.pool_size'),
             migrate_enabled=myconf.get('db.migrate'),
             check_reserved=['all'])
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = ['*'] if request.is_local else []
# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = myconf.get('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.get('forms.separator') or ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

from gluon.tools import Auth, Service, PluginManager

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=myconf.get('host.names'))

def user_bar():
    action = '/user'
    if auth.user:
        logout=A('logout', URL('test'))
        profile=A('profile', _href=action+'/profile')
        password=A('change password', _href=action+'/change_password')
        bar = SPAN(auth.user.email, ' | ', profile, ' | ', password, ' | ', logout, _class='auth_navbar')
    else:
        login=A('login', _href=action+'/login')
        lost_password=A('lost password', _href=action+'/request_reset_password')
        bar = SPAN(' ', login, ' | ', register, ' | ', lost_password, _class='auth_navbar')
    return bar

auth.settings.extra_fields['auth_user']= [ Field('permission', 'integer', length=3, default=0, readable=False, writable=False), Field('address', 'string'), Field('city', 'string'), Field('state_abbrev', 'string', length=2), Field('zip', 'integer', length=10)]

service = Service()
plugins = PluginManager()

# -------------------------------------------------------------------------
# create all tables needed by auth if not custom tables
# -------------------------------------------------------------------------
auth.define_tables(username=False, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.get('smtp.server')
mail.settings.sender = myconf.get('smtp.sender')
mail.settings.login = myconf.get('smtp.login')
mail.settings.tls = myconf.get('smtp.tls') or False
mail.settings.ssl = myconf.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------
db.define_table('courses2', Field('course_number', 'string', requires=IS_UPPER(), label = 'Course'), Field('course_name', 'string', label = 'Title'), Field('description', 'text'), Field('fall', 'boolean'), Field('winter', 'boolean'), Field('spring', 'boolean'), Field('summer', 'boolean'), Field('prereqs', 'list:reference courses2', requires=IS_IN_DB(db, 'courses2', label='%(course_number)s', multiple=True)), Field('area', 'list:integer', requires=IS_IN_SET([(1,'Introductory'),(2,'Foundation'),(3,'Software and Systems Development'),(4,'Theory'),(5,'Database Systems'),(6,'Software Engineering'),(7,'Data Science'),(8,'Artificial Intelligence'),(9,'Multimedia')],multiple=True)), migrate=False, fake_migrate=False)

# db.define_table('courses2', Field('course_number', 'string', requires=IS_UPPER(), label = 'Course'), Field('course_name', 'string', label = 'Title'), Field('description', 'text'), Field('fall', 'boolean'), Field('winter', 'boolean'), Field('spring', 'boolean'), Field('summer', 'boolean'), Field('prereqs', 'list:reference courses2', requires=IS_IN_DB(db, 'courses2', label='%(course_number)s', multiple=True)), Field('area', 'list:integer','boolean', requires=IS_IN_SET([(1,'Introductory'),(2,'Foundation'),(3,'Software and Systems Development'),(4,'Theory'),(5,'Database Systems'),(6,'Software Engineering'),(7,'Data Science'),(8,'Artificial Intelligence'),(9,'Multimedia')],multiple=True)), migrate=False, fake_migrate=False)



#Field('prereqs', 'list:reference courses2', requires=IS_IN_DB(db, 'courses2', label='%(course_number)s', multiple=True)), Field('area', 'list:reference sections', requires=IS_IN_DB(db, 'sections', label='%(description)s', multiple=True)), migrate=False, fake_migrate=False)
#db.define_table('course_quarter_availability_option', Field('availability_option', 'string'),format='%(availability_option)s')


#db.define_table('course_setting_availability_option', Field('availability_option', 'string'),format='%(availability_option)s')

#db.define_table('courses', Field('course_name', 'string'), Field('course_number', 'integer'), Field('course_title', 'string'), Field('course_description', 'text'),  Field('course_quarter_availability','reference course_quarter_availability_option', default=15, requires = IS_IN_DB(db, db.course_quarter_availability_option.id, '%(availability_option)s', zero=None),represent=lambda id, r: db.course_quarter_availability_option[id].availability_option), Field('course_setting_availability','reference course_setting_availability_option', requires = IS_IN_DB(db, db.course_setting_availability_option.id, '%(availability_option)s', zero=None),represent=lambda id, r: db.course_setting_availability_option[id].availability_option),migrate=False, fake_migrate=False)

#db.define_table('prerequisites', Field('course_id', requires = IS_IN_DB(db, db.courses.id, '%(course_name)s'+' '+'%(course_number)s', zero=None),represent=lambda id, r: '%s %d' %(db.courses[id].course_name, db.courses[id].course_number)), Field('prerequisite_course_id', 'reference courses', requires = IS_IN_DB(db, db.courses.id, '%(course_name)s'+' '+'%(course_number)s', zero=None), represent=lambda id, r: '%s %d' %(db.courses[id].course_name, db.courses[id].course_number)), migrate=False, fake_migrate=False)

#db.define_table('users', Field('first_name', 'string'), Field('last_name', 'string'), Field('permission', 'integer'),Field('faculty_advisor','reference users'),required=False)

#db.define_table('concentration', Field('concentration_name', 'string'), Field('concentration_specialization', 'string'), Field('concentration_group', #'string', default=1, requires=IS_IN_SET([1,2,3], labels=[T('Student'), T('Faculty'), T('Admin')], zero=None)), Field('concentration_open_elective', #'string'))

db.define_table('student_courses_taken', Field('user_id', 'reference auth_user'), Field('taken', 'list:reference courses2'))


# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
auth.enable_record_versioning(db)

#db.define_table('sections', Field('description', 'string'), Field('courses', 'list:reference courses2'))
db.define_table('sections', Field('description', 'string'))

#db.define_table('concentration_courses', Field('concentration_id', db.concentration), Field('course_id', db.courses), migrate=False, fake_migrate=False)

#db.define_table('prerequisites', Field('course_id', db.courses), Field('prerequisite_course_id', 'integer'), migrate=False, fake_migrate=False)

#db.define_table('student_courses', Field('user_id', db.auth_user), Field('course_id', 'integer'), Field('status', 'string'), migrate=False, fake_migrate=False)

#db.define_table('faculty_advisee', Field('faculty_user_id', db.auth_user), Field('student_user_id', db.auth_user), migrate=False, fake_migrate=False)

db.define_table('paths_saved', Field('student_id', db.auth_user), Field('course_path', 'json'), Field('path_name', 'string'), Field('start_quarter', 'string'),Field('date_created', 'datetime', default=request.now))

db.define_table('student', Field('student_id', db.auth_user), Field('faculty_id', db.auth_user))

db.define_table('faculty', Field('id', db.auth_user))

db.define_table('administrator', Field('admin_id', db.auth_user))

db.define_table('course_approval', Field('student_id', db.auth_user), Field('faculty_id', db.auth_user), Field('course_id', db.courses2))


# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
auth.enable_record_versioning(db)
