# -*- coding: utf-8 -*-
# try something like
import random
import json
import Queue
import datetime

def index(): return dict(message="hello from path.py")


def view_path():
    path_id = long(request.vars['path_id'])
    id = long(request.vars['id'])
    start = request.vars['start']
    path = request.vars['path']
    if auth.user.id == id or auth.user.permission > 0:
        form1=FORM(INPUT(_type="Submit", _value="Delete Path"))
        if form1.process(formname='form_one').accepted:
            del db.paths_saved[path_id]
            session.flash = "Path deleted."
            redirect(URL(c='student', f='index'))
        elif form1.errors:
            response.flash = "Error! Path not deleted"
        return dict(start=start, path=path, id=id, quarter=next_quarter, delete=form1)
    else:
        redirect(URL(c='user', f='not_authorized'))

def select_electives():
    area = request.vars['area']
    concentration = request.vars['concen']
    return dict(area=area, concentration=concentration)

def create_path():
    return dict(form="Create path")

def create_json(classes, starting_quarter, classes_per_quarter):
    start_quarter = starting_quarter.split()[0]
    current_quarter = start_quarter
    year = int(starting_quarter.split()[1])

    q = Queue.Queue()

    path = {}
    for course in classes:
        q.put(course)
    while not q.empty():
        quarter_classes = []
        for j in range(classes_per_quarter):
            if not q.empty():
                quarter_classes.append(q.get())
            path[current_quarter + " " + str(year)] = quarter_classes
        current_quarter = next_quarter(current_quarter)
        if (current_quarter == start_quarter):
            year += 1
    json_data = json.dumps(path)
    return json_data

def next_quarter(quarter):
    if quarter == "Winter":
        return "Spring"
    elif quarter == "Spring":
        return "Fall"
    elif quarter == "Fall":
        return "Winter"


def check_if_next_quarter(classes, quarter, classes_per_quarter):
    if len(classes) % classes_per_quarter == 0:
        return next_quarter(quarter)
    else:
        return quarter

def area_to_string(area):
    if area == 3:
        return "Software and Systems Development"
    elif area == 4:
        return "Theory"
    elif area == 5:
        return "Database Systems"
    elif area == 6:
        return "Software Engineering"
    elif area == 7:
        return "Data Science"
    elif area == 8:
        return "Artifical Intelligence"
    else:
        return "Multimedia"


def concen_to_int(concen):
    if concen == "Business Intelligence":
        return 12
    elif concen == "Business Analysis/Systems Analysis":
        return 14
    elif concen == "Database Administration":
        return 17
    elif concen == "IT Enterprise Management":
        return 19
    else:
        -1
        
def concen_to_advanced(concen):
    if concen == "Business Intelligence":
        return 4
    elif concen == "Business Analysis/Systems Analysis":
        return 5
    elif concen == "Database Administration":
        return 4
    elif concen == "IT Enterprise Management":
        return 4
    else:
        0
    
def created_path():
    degree = request.vars['degree']
    starting_quarter = str(request.vars['start'])
    classes_per_quarter = int(request.vars['classes'])
    class_delivery = request.vars['delivery']
    path = []
    form1=FORM(INPUT(_type="Submit", _value="Save Path"))
    if request.vars['concen'] != None:
        concentration = request.vars['concen']
        max = int(request.vars['max'])
        path = shortest_path_is(starting_quarter, concentration, classes_per_quarter, max)
        path_json = create_json(path, starting_quarter, classes_per_quarter)
        if form1.process(formname='form_one').accepted:
            date = datetime.date.today()
            path_name = degree + " (" + concentration + ") - " + str(date) + " - " + starting_quarter
            db.paths_saved.insert(student_id=auth.user_id, course_path=path_json, path_name=path_name, start_quarter=starting_quarter)
            response.flash = "Path saved."
        elif form1.errors:
            response.flash = "Error! Path not saved."
        return dict(degree=degree, concentration=concentration, start=starting_quarter.split()[0], year=starting_quarter.split()[1], quarter=next_quarter, classes=classes_per_quarter, delivery=class_delivery, concen=concentration, max=max,  path=path_json, submit=form1)
    else:
        area = int(request.vars['area'])
        area_classes = request.vars['area_classes'].split(",")
        other_classes = request.vars['other_classes'].split(",")
        area_name = area_to_string(area)
        path = shortest_path_compsci(starting_quarter, area, classes_per_quarter, area_classes, other_classes)
        path_json = create_json(path, starting_quarter, classes_per_quarter)
        if form1.process(formname='form_one').accepted:
            date = datetime.date.today()
            path_name = degree + " (" + area_name + ") - " + str(date) + " - " + starting_quarter
            db.paths_saved.insert(student_id=auth.user_id, course_path=path_json, path_name=path_name, start_quarter=starting_quarter)
            response.flash = "Path saved."
        elif form1.errors:
            response.flash = "Error! Path not saved."
        return dict(start=starting_quarter.split()[0], year=starting_quarter.split()[1], classes=classes_per_quarter, quarter=next_quarter, path=path_json, submit=form1)

def only_offered_winter(course):
    return course.winter == True and course.fall == False and course.spring == False

def only_offered_spring(course):
    return course.spring == True and course.fall == False and course.winter == False

def only_offered_fall(course):
    return course.fall == True and course.spring== False and course.winter == False

def check_current_quarter(classes,current, cpq):
    if len(current) == cpq:
        classes.extend(current)
        del current[:]

def check_area_count(check, area):
    if area in check.area and area < 4:
        return True
    return False

def is_path(classes, concen, quarter, classes_per_quarter, max):
    area = concen_to_int(concen)
    advanced_courses = db((db.courses2.area.contains(area))).select()
    open_courses = db((db.courses2.area.contains([3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]) & (~db.courses2.area.contains(area)))).select()
    area_courses = db(db.courses2.area.contains(area+1)).select()
    open_courses.exclude(lambda r: long(r.id) == 28 or long(r.id) == 29 or long(r.id) == 82 or long(r.id) == 83)
    open_courses.exclude(lambda r: long(r.id) == 118)
    capstone = db(db.courses2.id == 98).select()

    winter_queue = Queue.Queue()
    spring_queue = Queue.Queue()
    fall_queue  = Queue.Queue()

    for course in area_courses:
        if only_offered_winter(course):
            winter_queue.put(course.id)
        elif only_offered_spring(course):
            spring_queue.put(course.id)
        elif only_offered_fall(course):
            fall_queue.put(course.id)

    advanced_classes = 0
    major_classes = 0
    capstone_classes = 0

    max_advanced = concen_to_advanced(concen)
    
    current_quarter_classes = []

    while (major_classes + advanced_classes + capstone < 7) and major_classes < max or other_classes < 4:

        if len(current_quarter_classes) == classes_per_quarter:
            classes.extend(current_quarter_classes)
            del current_quarter_classes[:]


        random_index = random.randint(0, len(other_courses)-1)
        random_course = other_courses[random_index]
        prereqs = []
        if random_course.prereqs != []:
            for course in random_course.prereqs:
                prereqs.append(long(course.id))
            if set(prereqs).issubset(classes):
                if quarter == "Winter":
                    if not winter_queue.empty():
                        current_quarter_classes.append(winter_queue.get())
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if area_classes < 4:
                            area_classes += 1
                        else:
                            other_classes += 1
                    else:
                        if random_course.winter == True:
                            if random_course.id not in classes:
                                current_quarter_classes.append(random_course.id)
                                other_courses.exclude(lambda r: r.id == random_course.id)
                                quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                                if random_course.area == area and area_classes < 4:
                                    area_classes += 1
                                else:
                                    other_classes += 1
                elif quarter == "Spring":
                    if not spring_queue.empty():
                        current_quarter_classes.append(spring_queue.get())
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if area_classes < 4:
                            area_classes += 1
                        else:
                            other_classes += 1
                    else:
                        if random_course.spring == True:
                            if random_course.id not in classes:
                                current_quarter_classes.append(random_course.id)
                                other_courses.exclude(lambda r: r.id == random_course.id)
                                quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                                if random_course.area == area and area_classes < 4:
                                    area_classes += 1
                                else:
                                    other_classes += 1
                elif quarter == "Fall":
                    if not fall_queue.empty():
                        current_quarter_classes.append(fall_queue.get())
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if area_classes < 4:
                            area_classes += 1
                        else:
                            other_classes += 1
                    else:
                        if random_course.fall == True:
                            if random_course.id not in classes:
                                current_quarter_classes.append(random_course.id)
                                other_courses.exclude(lambda r: r.id == random_course.id)
                                quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                                if random_course.area == area and area_classes < 4:
                                    area_classes += 1
                                else:
                                    other_classes += 1

        else:
            if quarter == "Winter":
                if not winter_queue.empty():
                    current_quarter_classes.append(winter_queue.get())
                    if area_classes < 4:
                        area_classes += 1
                    else:
                        other_classes += 1
                else:
                    if random_course.winter == True:
                        current_quarter_classes.append(random_course.id)
                        other_courses.exclude(lambda r: r.id == random_course.id)
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if random_course.area == area and area_classes < 4:
                            area_classes += 1
                        else:
                            other_classes += 1
            elif quarter == "Spring":
                if not spring_queue.empty():
                    current_quarter_classes.append(spring_queue.get())
                    if area_classes < 4:
                        area_classes += 1
                    else:
                        other_classes += 1
                else:
                    if random_course.spring == True:
                        current_quarter_classes.append(random_course.id)
                        other_courses.exclude(lambda r: r.id == random_course.id)
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if random_course.area == area and area_classes < 4:
                            area_classes += 1
                        else:
                            other_classes += 1
            elif quarter == "Fall":
                if not fall_queue.empty():
                    current_quarter_classes.append(winter_queue.get())
                    if area_classes < 4:
                        area_classes += 1
                    else:
                        other_classes += 1
                else:
                    if random_course.fall == True:
                        current_quarter_classes.append(random_course.id)
                        other_courses.exclude(lambda r: r.id == random_course.id)
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if random_course.area == area and area_classes < 4:
                            area_classes += 1
                        else:
                            other_classes += 1

    if current_quarter_classes:
        classes.extend(current_quarter_classes)
    return quarter


def working_path(classes, area, quarter, classes_per_quarter):
    other_courses = db((db.courses2.area.contains([3,4,5,6,7,8,9]) & (~db.courses2.area.contains(area)))).select()
    area_courses = db(db.courses2.area.contains(area)).select()
    other_courses.exclude(lambda r: long(r.id) == 28 or long(r.id) == 29 or long(r.id) == 82 or long(r.id) == 83)
    other_courses.exclude(lambda r: long(r.id) == 118)

    winter_queue = Queue.Queue()
    spring_queue = Queue.Queue()
    fall_queue  = Queue.Queue()

    for course in area_courses:
        if only_offered_winter(course):
            winter_queue.put(course.id)
        elif only_offered_spring(course):
            spring_queue.put(course.id)
        elif only_offered_fall(course):
            fall_queue.put(course.id)

    area_classes = 0
    other_classes = 0

    current_quarter_classes = []

    while (area_classes + other_classes < 8) and area_classes < 4 or other_classes < 4:

        if len(current_quarter_classes) == classes_per_quarter:
            classes.extend(current_quarter_classes)
            del current_quarter_classes[:]


        random_index = random.randint(0, len(other_courses)-1)
        random_course = other_courses[random_index]
        prereqs = []
        if random_course.prereqs != []:
            for course in random_course.prereqs:
                prereqs.append(long(course.id))
            if set(prereqs).issubset(classes):
                if quarter == "Winter":
                    if not winter_queue.empty():
                        current_quarter_classes.append(winter_queue.get())
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if area_classes < 4:
                            area_classes += 1
                        else:
                            other_classes += 1
                    else:
                        if random_course.winter == True:
                            if random_course.id not in classes:
                                current_quarter_classes.append(random_course.id)
                                other_courses.exclude(lambda r: r.id == random_course.id)
                                quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                                if random_course.area == area and area_classes < 4:
                                    area_classes += 1
                                else:
                                    other_classes += 1
                elif quarter == "Spring":
                    if not spring_queue.empty():
                        current_quarter_classes.append(spring_queue.get())
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if area_classes < 4:
                            area_classes += 1
                        else:
                            other_classes += 1
                    else:
                        if random_course.spring == True:
                            if random_course.id not in classes:
                                current_quarter_classes.append(random_course.id)
                                other_courses.exclude(lambda r: r.id == random_course.id)
                                quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                                if random_course.area == area and area_classes < 4:
                                    area_classes += 1
                                else:
                                    other_classes += 1
                elif quarter == "Fall":
                    if not fall_queue.empty():
                        current_quarter_classes.append(fall_queue.get())
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if area_classes < 4:
                            area_classes += 1
                        else:
                            other_classes += 1
                    else:
                        if random_course.fall == True:
                            if random_course.id not in classes:
                                current_quarter_classes.append(random_course.id)
                                other_courses.exclude(lambda r: r.id == random_course.id)
                                quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                                if random_course.area == area and area_classes < 4:
                                    area_classes += 1
                                else:
                                    other_classes += 1

        else:
            if quarter == "Winter":
                if not winter_queue.empty():
                    current_quarter_classes.append(winter_queue.get())
                    if area_classes < 4:
                        area_classes += 1
                    else:
                        other_classes += 1
                else:
                    if random_course.winter == True:
                        current_quarter_classes.append(random_course.id)
                        other_courses.exclude(lambda r: r.id == random_course.id)
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if random_course.area == area and area_classes < 4:
                            area_classes += 1
                        else:
                            other_classes += 1
            elif quarter == "Spring":
                if not spring_queue.empty():
                    current_quarter_classes.append(spring_queue.get())
                    if area_classes < 4:
                        area_classes += 1
                    else:
                        other_classes += 1
                else:
                    if random_course.spring == True:
                        current_quarter_classes.append(random_course.id)
                        other_courses.exclude(lambda r: r.id == random_course.id)
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if random_course.area == area and area_classes < 4:
                            area_classes += 1
                        else:
                            other_classes += 1
            elif quarter == "Fall":
                if not fall_queue.empty():
                    current_quarter_classes.append(winter_queue.get())
                    if area_classes < 4:
                        area_classes += 1
                    else:
                        other_classes += 1
                else:
                    if random_course.fall == True:
                        current_quarter_classes.append(random_course.id)
                        other_courses.exclude(lambda r: r.id == random_course.id)
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if random_course.area == area and area_classes < 4:
                            area_classes += 1
                        else:
                            other_classes += 1

    if current_quarter_classes:
        classes.extend(current_quarter_classes)
    return quarter

def create_classes_path(classes, quarter, area, classes_per_quarter, area_classes, other_classes):

    electives = []
    
    quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)

    for course in area_classes:
        if course != ",":
            electives.append(course)

    for course in other_classes:
        if course != ",":
            electives.append(course)

    winter_queue = Queue.Queue()
    spring_queue = Queue.Queue()
    fall_queue  = Queue.Queue()

    remove_electives = []
    for course_id in electives:
        course = db(db.courses2.id == course_id).select()[0]
        if only_offered_winter(course):
            winter_queue.put(long(course.id))
            remove_electives.append(long(course.id))

        elif only_offered_spring(course):
            spring_queue.put(long(course.id))
            remove_electives.append(long(course.id))

        elif only_offered_fall(course):
            fall_queue.put(long(course.id))
            remove_electives.append(long(course.id))



    area_classes = 0
    other_classes = 0


    current_quarter_classes = []

    while (area_classes + other_classes < 8) and area_classes < 4 or other_classes < 4:

        check_current_quarter(classes, current_quarter_classes, classes_per_quarter)

        course = electives[0]
        course_info = db(db.courses2.id == course).select()[0]
        prereqs = []
        if course_info.prereqs != []:
            for course in course_info.prereqs:
                prereqs.append(long(course.id))
            if set(prereqs).issubset(classes):
                if quarter == "Fall":
                    if not fall_queue.empty():
                        deq = fall_queue.get()
                        check = db(db.courses2.id == deq).select()[0]
                        current_quarter_classes.append(deq)
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if check_area_count(check, area):
                            area_classes += 1
                        else:
                            other_classes += 1
                    else:
                        if course_info.fall == True:
                            if course_info.id not in classes:
                                current_quarter_classes.append(course_info.id)
                                electives.pop(0)
                                quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                                if check_area_count(check, area):
                                    area_classes += 1
                                else:
                                    other_classes += 1
                        else:
                            for course in electives[1:]:
                                course_in = db(db.courses2.id == course).select()[0]
                                if course_in.fall == True:
                                    current_quarter_classes.append(long(course_in.id))
                                    if check_area_count(course_in, area):
                                        area_classes += 1
                                    else:
                                        other_classes += 1
                                    break
                            else:
                                current_quarter_classes.append(118)
                elif quarter == "Spring":
                    if not spring_queue.empty():
                        deq = spring_queue.get()
                        check = db(db.courses2.id == deq).select()[0]
                        current_quarter_classes.append(deq)
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if check_area_count(check, area):
                            area_classes += 1
                        else:
                            other_classes += 1
                    else:
                        if course_info.spring == True:
                            if course_info.id not in classes:
                                current_quarter_classes.append(course_info.id)
                                electives.pop(0)
                                quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                                if check_area_count(check, area):
                                    area_classes += 1
                                else:
                                    other_classes += 1
                        else:
                            for course in electives[1:]:
                                course_in = db(db.courses2.id == course).select()[0]
                                if course_in.spring == True:
                                    current_quarter_classes.append(long(course_in.id))
                                    if check_area_count(course_in, area):
                                        area_classes += 1
                                    else:
                                        other_classes += 1
                                    break
                            else:
                                current_quarter_classes.append(118)
                else:
                    if not winter_queue.empty():
                        deq = winter_queue.get()
                        check = db(db.courses2.id == deq).select()[0]
                        current_quarter_classes.append(deq)
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if check_area_count(check, area):
                            area_classes += 1
                        else:
                            other_classes += 1
                    else:
                        if course_info.winter == True:
                            if course_info.id not in classes:
                                current_quarter_classes.append(course_info.id)
                                electives.pop(0)
                                quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                                if check_area_count(check, area):
                                    area_classes += 1
                                else:
                                    other_classes += 1
                        else:
                            for course in electives[1:]:
                                course_in = db(db.courses2.id == course).select()[0]
                                if course_in.winter == True:
                                    current_quarter_classes.append(long(course_in.id))
                                    if check_area_count(course_in, area):
                                        area_classes += 1
                                    else:
                                        other_classes += 1
                                    break
                            else:
                                current_quarter_classes.append(118)

    if current_quarter_classes:
        classes.extend(current_quarter_classes)
    return quarter


def intro_course_path(starting, area, classes, classes_per_quarter):
    intro_classes = db(db.courses2.area == 1).select()
    intro = []
    for course in intro_classes:
        intro.append(course.id)

def predefined_intro(classes_per_quarter):
    if classes_per_quarter == 1:
        return [1,2,3,5,4,6]
    elif classes_per_quarter == 2:
        return [1,2,3,5,4,6]
    else:
        return [1,2,118,3,5,118,4,6,118]

def predefined_is(cpq, concen):
    if concen == "Business Intelligence":
        if cpq == 1:
            return [74, 2]
        elif cpq == 2:
            return [74,2]
        else:
            cpq == [74,2]
    elif concen == "Database Administration":
        if cpq == 1:
            return [2]
        elif cpq == 2:
            return [2]
        else:
            return [2]
    else:
        return []
    
def insert_foundation_is(current_quarter, classes_per_quarter, classes_to_take):
    foundation_classes = db(db.courses2.area.contains(11)).select()
    foundation = []
    for course in foundation_classes:
        foundation.append(long(course.id))
    current_quarter_classes = []
    while foundation:
        if len(current_quarter_classes) == classes_per_quarter:
            classes_to_take.extend(current_quarter_classes)
            del current_quarter_classes[:]
            current_quarter = next_quarter(current_quarter)
        else:
            current_quarter_classes.append(foundation.pop(0))
    classes_to_take.extend(current_quarter_classes)
    return current_quarter

def insert_foundation_courses(current_quarter, classes_per_quarter, classes_to_take):
    foundation_classes = db(db.courses2.area.contains(2)).select()
    foundation = []
    for course in foundation_classes:
        foundation.append(long(course.id))
    current_quarter_classes = []
    while foundation:
        if len(current_quarter_classes) == classes_per_quarter:
            classes_to_take.extend(current_quarter_classes)
            del current_quarter_classes[:]
            current_quarter = next_quarter(current_quarter)
        else:
            current_quarter_classes.append(foundation.pop(0))
    classes_to_take.extend(current_quarter_classes)
    return current_quarter


def insert_intro_courses(starting_quarter, classes_per_quarter, classes_to_take):
    intro_classes = db(db.courses2.area.contains(1)).select()
    intro = []
    added = 0
    current_quarter = starting_quarter
    for course in intro_classes:
        intro.append(course.id)

    if auth.is_logged_in():
        student_courses = db(db.student_courses_taken.user_id == auth.user.id).select()

        classes_taken = []
        if len(student_courses) > 0:
            for course in student_courses[0].taken:
                classes_taken.append(long(course))

            current_quarter_classes = []
            while added < 6:
                if len(current_quarter_classes) == classes_per_quarter:
                    classes_to_take.extend(current_quarter_classes)
                    del current_quarter_classes[:]
                    current_quarter = next_quarter(current_quarter)
                course = intro[0]
                if course not in classes_taken:
                    course_info = db(db.courses2.id == course).select()
                    prereqs = []
                    for course in course_info[0].prereqs:
                        prereqs.append(long(course.id))
                    if set(prereqs).issubset(classes_to_take):
                        current_quarter_classes.append(intro.pop(0))
                        added += 1
                    else:
                        for i in range(len(intro)):
                            if len(current_quarter_classes) == classes_per_quarter:
                                classes_to_take.extend(current_quarter_classes)
                                del current_quarter_classes[:]
                            prereqs = []
                            course_info = db(db.courses2.id == intro[i]).select()
                            for course in course_info[0].prereqs:
                                prereqs.append(long(course.id))
                            if set(prereqs).issubset(classes_to_take):
                                current_quarter_classes.append(intro[i])
                                added += 1
                            elif i == len(intro)-1:
                                current_quarter_classes.append(118)
                else:
                    intro.pop(0)
                    added += 1
            classes_to_take.extend(current_quarter_classes)
            if classes_per_quarter == 3:
                classes_to_take.pop()
                classes_to_take.append(6)
            for course in classes_taken:
                if len(classes_to_take) % classes_per_quarter != 0:
                    classes_to_take.append(118)
            return starting_quarter
        else:
            classes_to_take.extend(predefined_intro(classes_per_quarter))
            starting_quarter = next_quarter(starting_quarter)
            starting_quarter = next_quarter(starting_quarter)
            return starting_quarter
    else:
        classes_to_take.extend(predefined_intro(classes_per_quarter))
        starting_quarter = next_quarter(starting_quarter)
        starting_quarter = next_quarter(starting_quarter)
        return starting_quarter


def shortest_path_is(starting, concen, classes_per_quarter, max):
    classes_to_take = [12,13,14,55,52,3,32,56,55,23,21,100]

    #current_quarter = starting.split()[0]
    #classes_to_take.extend(predefined_is(classes_per_quarter, concen))
    #insert_foundation_is(current_quarter, classes_per_quarter, classes_to_take)

    return classes_to_take



def shortest_path_compsci(starting, area, classes_per_quarter, area_classes, other_classes):
    classes_to_take = []

    current_quarter = starting.split()[0]
    insert_intro_courses(current_quarter, classes_per_quarter, classes_to_take)
    insert_foundation_courses(current_quarter, classes_per_quarter, classes_to_take)
    current_quarter = working_path(classes_to_take, area, current_quarter, classes_per_quarter)

    return classes_to_take

#German Test, DELETE IF NOT WORKING
'''
def shortest_path_compsci2(starting, area, classes_per_quarter, area_classes, other_classes):
    classes_to_take = []
    current quarter = starting.split()[0]
    insert_intro_courses(current_quarter, classes_per_quarter, classes_to_take)
    insert_foundation_courses(current_quarter, classes_per_quarter, classes_to_take)
    current quarter = working+path2(classes_to_take, area, current quarter, classes_per_quarter, area_classes, other_classes)
    
    return classes_to_take

def working_path2(required, area, quarter, classes_per_quarter, myarea, myelec):
    course_list = required
    for i in myarea:
        course_list.append(i)
    for i in myelec:
        course_list.append(i) 
    course_list.exclude(lambda r: long(r.id) == 28 or long(r.id) == 29 or long(r.id) == 82 or long(r.id) == 83)
    course_list.exclude(lambda r: long(r.id) == 118)

    for course in area_courses:
        if only_offered_winter(course):
            winter_queue.put(course.id)
        elif only_offered_spring(course):
            spring_queue.put(course.id)
        elif only_offered_fall(course):
            fall_queue.put(course.id)

    area_classes = 0
    other_classes = 0

    current_quarter_classes = []

    while (area_classes + other_classes < 8) and area_classes < 4 or other_classes < 4:

        if len(current_quarter_classes) == classes_per_quarter:
            classes.extend(current_quarter_classes)
            del current_quarter_classes[:]


        random_index = random.randint(0, len(other_courses)-1)
        random_course = other_courses[random_index]
        prereqs = []
        if random_course.prereqs != []:
            for course in random_course.prereqs:
                prereqs.append(long(course.id))
            if set(prereqs).issubset(classes):
                if quarter == "Winter":
                    if not winter_queue.empty():
                        current_quarter_classes.append(winter_queue.get())
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if area_classes < 4:
                            area_classes += 1
                        else:
                            other_classes += 1
                    else:
                        if random_course.winter == True:
                            if random_course.id not in classes:
                                current_quarter_classes.append(random_course.id)
                                other_courses.exclude(lambda r: r.id == random_course.id)
                                quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                                if random_course.area == area and area_classes < 4:
                                    area_classes += 1
                                else:
                                    other_classes += 1
                elif quarter == "Spring":
                    if not spring_queue.empty():
                        current_quarter_classes.append(spring_queue.get())
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if area_classes < 4:
                            area_classes += 1
                        else:
                            other_classes += 1
                    else:
                        if random_course.spring == True:
                            if random_course.id not in classes:
                                current_quarter_classes.append(random_course.id)
                                other_courses.exclude(lambda r: r.id == random_course.id)
                                quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                                if random_course.area == area and area_classes < 4:
                                    area_classes += 1
                                else:
                                    other_classes += 1
                elif quarter == "Fall":
                    if not fall_queue.empty():
                        current_quarter_classes.append(fall_queue.get())
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if area_classes < 4:
                            area_classes += 1
                        else:
                            other_classes += 1
                    else:
                        if random_course.fall == True:
                            if random_course.id not in classes:
                                current_quarter_classes.append(random_course.id)
                                other_courses.exclude(lambda r: r.id == random_course.id)
                                quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                                if random_course.area == area and area_classes < 4:
                                    area_classes += 1
                                else:
                                    other_classes += 1

        else:
            if quarter == "Winter":
                if not winter_queue.empty():
                    current_quarter_classes.append(winter_queue.get())
                    if area_classes < 4:
                        area_classes += 1
                    else:
                        other_classes += 1
                else:
                    if random_course.winter == True:
                        current_quarter_classes.append(random_course.id)
                        other_courses.exclude(lambda r: r.id == random_course.id)
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if random_course.area == area and area_classes < 4:
                            area_classes += 1
                        else:
                            other_classes += 1
            elif quarter == "Spring":
                if not spring_queue.empty():
                    current_quarter_classes.append(spring_queue.get())
                    if area_classes < 4:
                        area_classes += 1
                    else:
                        other_classes += 1
                else:
                    if random_course.spring == True:
                        current_quarter_classes.append(random_course.id)
                        other_courses.exclude(lambda r: r.id == random_course.id)
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if random_course.area == area and area_classes < 4:
                            area_classes += 1
                        else:
                            other_classes += 1
            elif quarter == "Fall":
                if not fall_queue.empty():
                    current_quarter_classes.append(winter_queue.get())
                    if area_classes < 4:
                        area_classes += 1
                    else:
                        other_classes += 1
                else:
                    if random_course.fall == True:
                        current_quarter_classes.append(random_course.id)
                        other_courses.exclude(lambda r: r.id == random_course.id)
                        quarter = check_if_next_quarter(classes, quarter, classes_per_quarter)
                        if random_course.area == area and area_classes < 4:
                            area_classes += 1
                        else:
                            other_classes += 1

    if current_quarter_classes:
        classes.extend(current_quarter_classes)
    return quarter

'''
