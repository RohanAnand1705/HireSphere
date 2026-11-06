from database import connect

def jobs(query='',location='',kind='Any'):
    sql="SELECT j.*,c.name company FROM Jobs j JOIN Companies c ON c.id=j.company_id WHERE j.status='Open'"
    args=[]
    if query: sql += ' AND (j.title LIKE ? OR c.name LIKE ?)'; args += [f'%{query}%',f'%{query}%']
    if location: sql += ' AND j.location LIKE ?'; args.append(f'%{location}%')
    if kind!='Any': sql += ' AND j.job_type=?'; args.append(kind)
    with connect() as c: return c.execute(sql+' ORDER BY j.created_at DESC',args).fetchall()

def create_job(user_id,data,job_id=None):
    if not data.get('title','').strip() or not data.get('description','').strip(): raise ValueError('Job title and description are required.')
    with connect() as c:
        company=c.execute('SELECT id FROM Companies WHERE user_id=?',(user_id,)).fetchone()
        if job_id:
            c.execute("UPDATE Jobs SET title=?,description=?,required_skills=?,preferred_skills=?,experience=?,salary=?,location=?,job_type=? WHERE id=? AND company_id=?",(*[data.get(k,'') for k in ('title','description','required_skills','preferred_skills','experience','salary','location','job_type')],job_id,company['id']))
        else:
            c.execute('INSERT INTO Jobs(company_id,title,description,required_skills,preferred_skills,experience,salary,location,job_type) VALUES(?,?,?,?,?,?,?,?,?)',(company['id'],*[data.get(k,'') for k in ('title','description','required_skills','preferred_skills','experience','salary','location','job_type')]))
