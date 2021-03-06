# -*- coding: utf-8 -*-
# try something like
if auth.user is None:
    redirect(URL('default/user','login', vars={'_next':URL(c='admin', f='index')}))

@auth.requires(auth.user.permission==2)
def index(): return dict(message="hello from admin.py")

@auth.requires(auth.user.permission==2)
def users():
    grid=SQLFORM.grid(db.auth_user)
    return dict(grid=grid)

def faculty_view():
    query = db.auth_user.permission==1
    grid=SQLFORM.grid(query, create=False, deletable=False, details=False, editable=False, csv=False, links = [lambda row: A('Impersonate',_class='button btn btn-default',_href=URL('faculty',"index",args=[row.id]))])
    return dict(grid=grid)

def student_view():
    query = db.auth_user.permission==0
    grid=SQLFORM.grid(query,create=False, deletable=False, details=False, editable=False, csv=False, links = [lambda row: A('Impersonate',_class='button btn btn-default',_href=URL('student',"index",args=[row.id]))])
    return dict(grid=grid)

@auth.requires(auth.user.permission==2)
def courses(): return dict(grid=db.courses2)

@auth.requires(auth.user.permission==2)
def degrees(): return dict(msg="Degrees")

@auth.requires(auth.user.permission==2)
def courses():
    grid=SQLFORM.grid(db.courses2, fields = [db.courses2.course_number, db.courses2.course_name], user_signature=False, deletable=True, details=True, editable=True, csv=False)
    return dict(grid=grid)

#links=[lambda row: A('Edit', _href=URL('manage_course', args=row.id),_class="button btn btn-default")]

#def manage_prerequisite():
#    course_id = request.args(0) or redirect(URL('courses'))
#    db.prerequisites.course_id.default = int(course_id)
#    db.prerequisites.course_id.writable = False
#    form = SQLFORM.grid(db.prerequisites.course_id == course_id,
#                       args=[course_id],
 #                      searchable=False,
 #                      editable=False,
 #                      deletable=True,
 #                      details=False,
 #                      selectable=False,
 #                      csv=False,
 #                      user_signature=False)
#    return form

#def course_view():
#    course_id = request.args(0) or redirect(URL('courses'))
#    db.courses.id.default = int(course_id)
#    form = crud.read(db.courses, id)
#    return form

#def manage_course():
#    id = request.args(0) or redirect(URL('courses'))
#    from gluon.tools import Crud
#    crud = Crud(db)
#    form = crud.read(db.courses, id)
#    prerequisite_panel = LOAD(request.controller,
#                            'manage_prerequisite',
#                             args=[id],
#                             ajax=True)
#    return dict(form=form,panel=prerequisite_panel)
