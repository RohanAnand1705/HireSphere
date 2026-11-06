import bcrypt
from database import connect

def register(name,email,password,role):
    name=name.strip(); email=email.strip().lower()
    if not name or '@' not in email or len(password)<8 or role not in ('applicant','recruiter'):
        raise ValueError('Enter a name, valid email, password of at least 8 characters, and a portal role.')
    digest=bcrypt.hashpw(password.encode(),bcrypt.gensalt())
    with connect() as c:
        cur=c.execute('INSERT INTO Users(name,email,password_hash,role) VALUES(?,?,?,?)',(name,email,digest,role)); uid=cur.lastrowid
        if role=='applicant': c.execute('INSERT INTO ApplicantProfiles(user_id) VALUES(?)',(uid,))
        else: c.execute('INSERT INTO Companies(user_id,name) VALUES(?,?)',(uid,name))
    return {'id':uid,'name':name,'email':email,'role':role}

def login(email,password,role):
    with connect() as c: u=c.execute('SELECT * FROM Users WHERE email=? AND role=?',(email.strip().lower(),role)).fetchone()
    if not u or not bcrypt.checkpw(password.encode(),u['password_hash']): raise ValueError('Email or password is incorrect.')
    return {'id':u['id'],'name':u['name'],'email':u['email'],'role':u['role']}
