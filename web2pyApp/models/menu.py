# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# Customize your APP title, subtitle and menus here
# ----------------------------------------------------------------------------------------------------------------------
response.logo = A(B('When-If Calculator'),
                  _class="navbar-brand",
                  _id="web2py-logo")

response.title = request.application.replace('_', ' ').title()
response.subtitle = ''

# ----------------------------------------------------------------------------------------------------------------------
# read more at http://dev.w3.org/html5/markup/meta.name.html
# ----------------------------------------------------------------------------------------------------------------------
response.meta.author = myconf.get('app.author')
response.meta.description = myconf.get('app.description')
response.meta.keywords = myconf.get('app.keywords')
response.meta.generator = myconf.get('app.generator')

# ----------------------------------------------------------------------------------------------------------------------
# your http://google.com/analytics id
# ----------------------------------------------------------------------------------------------------------------------
response.google_analytics_id = None

DEVELOPMENT_MENU = True


# ----------------------------------------------------------------------------------------------------------------------
# provide shortcuts for development. remove in production
# ----------------------------------------------------------------------------------------------------------------------
def _():
    # ------------------------------------------------------------------------------------------------------------------
    # shortcuts
    # ------------------------------------------------------------------------------------------------------------------
    app = request.application
    ctr = request.controller
    # ------------------------------------------------------------------------------------------------------------------
    # useful links to internal and external resources
    # ------------------------------------------------------------------------------------------------------------------
    response.login_menu = [(T('Log In'), False, URL('user', 'login'))]
    response.logout_menu = [(T('Log Out'), False, URL('user', 'logout', vars=dict(_next=URL('user', 'login'))))]


    if auth.is_logged_in():
        if auth.user.permission == 0:
            response.menu = [(T('Home'), False, URL('student', 'index'))]
        elif auth.user.permission == 1:
            response.menu = [(T('Home'), False, URL('faculty', 'index'))]
            response.menu += [(T('Approvals'), False, URL('faculty', 'index'))]
            response.menu += [(T('Students'), False, URL('faculty', 'view_students'))]
        else:
            response.menu = [(T('Home'), False, URL(c='admin', f='index'))]
            response.menu += [(T('Courses'), False, URL(c='admin', f='courses'))]
            response.menu += [(T('Users'), False, URL(c='admin', f='users'))]
            response.menu += [(T('Faculty View'), False, URL(c='admin', f='faculty_view'))]
            response.menu += [(T('Student View'), False, URL(c='admin', f='student_view'))]
#            response.menu += [(T('My Sites'), False, URL('admin', 'default', 'site')),
#                              (T('This App'), False, '#', [
#                        (T('Design'), False, URL('admin', 'default', 'design/%s' % app)),
#                        LI(_class="divider"),(T('Controller'), False,URL('admin', 'default', 'edit/%s/controllers/%s.py' % (app, ctr))),
#                        (T('View'), False,URL('admin', 'default', 'edit/%s/views/%s' % (app, response.view))),
#                        (T('DB Model'), False,URL('admin', 'default', 'edit/%s/models/db.py' % app)),
#                        (T('Menu Model'), False,URL('admin', 'default', 'edit/%s/models/menu.py' % app)),
#                        (T('Config.ini'), False,URL('admin', 'default', 'edit/%s/private/appconfig.ini' % app)),
#                        (T('Layout'), False,URL('admin', 'default', 'edit/%s/views/layout.html' % app)),
#                        (T('Stylesheet'), False,URL('admin', 'default', 'edit/%s/static/css/web2py-bootstrap3.css' % app)),
#                        (T('Database'), False, URL(app, 'appadmin', 'index')),(T('Errors'), False, URL('admin', 'default', 'errors/' + app)),
#                        (T('About'), False, URL('admin', 'default', 'about/' + app)),])]
            
    response.menu += [(T('Profile'), False, URL(c='default', f='user/profile'))]


if DEVELOPMENT_MENU:
    _()

if "auth" in locals():
    auth.wikimenu()
