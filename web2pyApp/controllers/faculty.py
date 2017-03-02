# -*- coding: utf-8 -*-
# try something like
if auth.user is None:
    redirect(URL('default/user','login', vars={'_next':URL(c='faculty', f='index')}))
@auth.requires(auth.user.permission==1 or auth.user.permission==2)
def index():
    form = FORM('Your name:', INPUT(_name='name'), INPUT(_type='submit'))
    #Grab data from course_approval table (only grabs current faculties students)
    get_approvals = db(db.auth_user.id == db.course_approval.faculty_id).select(db.auth_user.first_name, db.auth_user.last_name, db.course_approval.course_id, db.course_approval.student_id, db.course_approval.faculty_id)
    students = []
    for i in range(len(get_approvals)):
        students.append(db((db.auth_user.id == get_approvals[i].course_approval.student_id) & (get_approvals[i].course_approval.course_id == db.courses2.id)).select(db.auth_user.id, db.auth_user.first_name,
        db.auth_user.last_name, db.courses2.id, db.courses2.course_name, db.courses2.course_number))
    return dict(form=form, approvals=students)


def user():
    return dict(form=auth())


@auth.requires(auth.user.permission==1 or auth.user.permission==2)
def view_students():
	get_students = db(db.student.faculty_id == db.auth_user.id).select()
	students = []
	for i in range(len(get_students)):
		students.append(db(db.auth_user.id == get_students[i].student.student_id).select())
	return dict(users=students)


@auth.requires(auth.user.permission==1 or auth.user.permission==2)
def student():
    student_id = 0;
    if len(request.vars) == 1:
        student_id = long(request.vars['id'])
    else:
        student_id = long(request.vars['id'][0])
    student = db.auth_user(student_id)
    student_name = db(db.auth_user.id == student_id).select(db.auth_user.first_name, db.auth_user.last_name)
    profile_form = SQLFORM(db.auth_user, student)
    if profile_form.process().accepted:
        response.flash = "User updated."
    elif profile_form.errors:
        response.flash = "Form has errors. User not updated."
    return dict(profile=profile_form, name=student_name, id=student_id)

@auth.requires(auth.user.permission==1 or auth.user.permission==2)
def approval():
    student_id = long(request.vars['student_id'])
    course_id = long(request.vars['course_id'])
    course_info = db(db.courses2.id == course_id).select()
    student_name = db(db.auth_user.id == student_id).select(db.auth_user.first_name, db.auth_user.last_name)
    student = db(db.auth_user.id == student_id).select()
    form1=FORM(INPUT(_type="Submit", _value="Approve"))
    if form1.process(formname='form_one').accepted:
        db.student_courses.insert(user_id=student_id, course_id=course_id, status="In-Progress")
        db((db.course_approval.course_id == course_id) & (db.course_approval.student_id == student_id)).delete()
        session.flash = "Student request approved."
        redirect(URL(c="faculty", f="index"))
    elif form1.errors:
        session.flash = "Error."
    form2=FORM(INPUT(_type="Submit", _value="Deny"))
    if form2.process(formname='form_two').accepted:
        db((db.course_approval.course_id == course_id) & (db.course_approval.student_id == student_id)).delete()
        session.flash = "Student request denied."
        redirect(URL(c="faculty", f="index"))
    elif form2.errors:
        session.flash = "Error."
    return dict(course=course_info, name=student_name, student=student, form1=form1, form2=form2)
