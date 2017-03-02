# -*- coding: utf-8 -*-
# try something like

if auth.user is None:
    redirect(URL('default/user','login', vars={'_next':URL(c='student', f='index')}))
def index():
    if auth.user.permission == 2:
        url = request.url
        stud_id = url[len(url)-1]
        paths = db(db.paths_saved.student_id == stud_id).select()
        return dict(paths=paths)
    else:
        paths = db(db.paths_saved.student_id == auth.user.id).select()
        return dict(paths=paths, id=request.vars)


def paths():
    student_id = long(request.vars['id'])
    if auth.user.id != student_id and auth.user.permission < 1:
        redirect(URL(c='user', f='not_authorized'))
    else:
        student_info = db(db.auth_user.id == student_id).select()
        paths = db(db.paths_saved.student_id == student_id).select()
        return dict(paths=paths, id=student_id, student=student_info)
