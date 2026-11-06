"""HireSphere AI: native Tkinter recruitment and career desktop app."""
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
try:
    import customtkinter as ctk
    ctk.set_appearance_mode('light'); ctk.set_default_color_theme('blue'); Base=ctk.CTk
except ImportError:
    ctk=None; Base=tk.Tk
import database
from database import connect
from services import auth_service, job_service, application_service
from services.resume_parser import parse_pdf
from services.matching_engine import score_resume
from services import interview_service

BG='#f5f6fb'; INK='#1c2040'; MUTED='#777d95'; PURPLE='#6258d9'; CARD='#ffffff'; DARK=False

class HireSphere(Base):
    def __init__(self):
        super().__init__(); self.title('HireSphere AI | Your Career. Smarter Connections.'); self.geometry('1200x760'); self.minsize(900,620); self.configure(bg=BG)
        self.user=None; self.current='Dashboard'; self.protocol('WM_DELETE_WINDOW',self.destroy); self.show_auth()
    def clear(self):
        for w in self.winfo_children(): w.destroy()
    def label(self,parent,text,size=12,bold=False,color=INK,**kw):
        if ctk:
            bg=kw.pop('bg',None)
            if bg:kw['fg_color']=bg
            return ctk.CTkLabel(parent,text=text,font=('Segoe UI',size,'bold' if bold else 'normal'),text_color=color,**kw)
        return tk.Label(parent,text=text,font=('Segoe UI',size,'bold' if bold else 'normal'),fg=color,bg=parent.cget('bg') if 'bg' not in kw else kw['bg'],**{k:v for k,v in kw.items() if k!='bg'})
    def button(self,parent,text,cmd,primary=False):
        secondary='#35364d' if DARK else '#ecebff'
        if ctk: return ctk.CTkButton(parent,text=text,command=cmd,fg_color=PURPLE if primary else secondary,text_color='white' if primary or DARK else PURPLE,corner_radius=9,height=36)
        return tk.Button(parent,text=text,command=cmd,bg=PURPLE if primary else secondary,fg='white' if primary or DARK else PURPLE,relief='flat',padx=14,pady=8)
    def entry(self,parent,placeholder='',show=None):
        if ctk: return ctk.CTkEntry(parent,placeholder_text=placeholder,show=show,height=38)
        return tk.Entry(parent,show=show,font=('Segoe UI',11),relief='solid',bd=1)
    def show_auth(self,register=False):
        self.clear(); outer=tk.Frame(self,bg=BG); outer.pack(fill='both',expand=True); card=tk.Frame(outer,bg=CARD,padx=50,pady=38,highlightbackground='#e4e5ef',highlightthickness=1); card.place(relx=.5,rely=.5,anchor='center',width=460)
        self.label(card,'◈  HireSphere AI',24,True,PURPLE,bg=CARD).pack(anchor='w'); self.label(card,'Your Career. Smarter Connections.',11,False,MUTED,bg=CARD).pack(anchor='w',pady=(2,24))
        self.label(card,'Create your account' if register else 'Welcome back',20,True,bg=CARD).pack(anchor='w',pady=(0,16))
        self.auth_fields={}
        fields=([('name','Full name',None)] if register else [])+[('email','Email address',None),('password','Password','•')]
        for key,hint,show in fields:
            self.label(card,hint,10,True,MUTED,bg=CARD).pack(anchor='w',pady=(6,4)); e=self.entry(card,hint,show); e.pack(fill='x'); self.auth_fields[key]=e
        self.label(card,'Portal',10,True,MUTED,bg=CARD).pack(anchor='w',pady=(12,5)); self.role=tk.StringVar(value='Applicant')
        if ctk: ctk.CTkSegmentedButton(card,values=['Applicant','Recruiter'],variable=self.role).pack(fill='x',pady=(0,15))
        else:
            row=tk.Frame(card,bg=CARD); row.pack(anchor='w'); tk.Radiobutton(row,text='Applicant',variable=self.role,value='Applicant',bg=CARD).pack(side='left'); tk.Radiobutton(row,text='Recruiter',variable=self.role,value='Recruiter',bg=CARD).pack(side='left')
        self.button(card,'Create account' if register else 'Sign in',self.do_register if register else self.do_login,True).pack(fill='x',pady=(8,12))
        self.button(card,'Already registered? Sign in' if register else 'New to HireSphere? Create account',lambda:self.show_auth(not register)).pack(fill='x')
    def do_register(self):
        try: self.user=auth_service.register(self.auth_fields['name'].get(),self.auth_fields['email'].get(),self.auth_fields['password'].get(),self.role.get().lower()); self.show_app()
        except Exception as e: messagebox.showerror('Registration',str(e))
    def do_login(self):
        try: self.user=auth_service.login(self.auth_fields['email'].get(),self.auth_fields['password'].get(),self.role.get().lower()); self.show_app()
        except Exception as e: messagebox.showerror('Sign in',str(e))
    def navitems(self):
        return ['Dashboard','Find Jobs','Saved Jobs','My Applications','Resume Analyzer','Mock Interview','Career Guidance','My Profile','Settings'] if self.user['role']=='applicant' else ['Dashboard','Post a Job','Manage Jobs','Applications','Candidate Screening','Shortlisted Candidates','Interviews','Analytics','Company Profile','Settings']
    def show_app(self,page='Dashboard'):
        self.current=page; self.clear(); self.configure(bg=BG)
        sidebar='#171827' if DARK else '#20213b'; side=tk.Frame(self,bg=sidebar,width=225); side.pack(side='left',fill='y'); side.pack_propagate(False)
        self.label(side,'◈  HireSphere',19,True,'white',bg=sidebar).pack(anchor='w',padx=20,pady=(26,2)); self.label(side,'CAREER & TALENT PLATFORM',8,True,'#a4a6c3',bg=sidebar).pack(anchor='w',padx=22,pady=(0,24))
        self.label(side,self.user['name'],12,True,'white',bg=sidebar).pack(anchor='w',padx=20); self.label(side,self.user['role'].title()+' portal',10,False,'#a4a6c3',bg=sidebar).pack(anchor='w',padx=20,pady=(2,18))
        for item in self.navitems():
            active='#363650' if not DARK else '#34354d';b=tk.Button(side,text=('  '+item),anchor='w',command=lambda p=item:self.show_app(p),bg=active if item==page else sidebar,fg='white' if item==page else '#c5c6d8',activebackground=active,activeforeground='white',relief='flat',bd=0,padx=16,pady=10,font=('Segoe UI',10)); b.pack(fill='x',padx=10,pady=1)
        self.button(side,'Log out',self.logout).pack(side='bottom',fill='x',padx=16,pady=18)
        main=tk.Frame(self,bg=BG); main.pack(side='left',fill='both',expand=True); top=tk.Frame(main,bg=BG); top.pack(fill='x',padx=32,pady=(24,10)); self.label(top,page,23,True,bg=BG).pack(side='left'); self.label(top,datetime.now().strftime('%A, %d %B'),10,False,MUTED,bg=BG).pack(side='right')
        shell=tk.Frame(main,bg=BG);shell.pack(fill='both',expand=True,padx=32,pady=12);canvas=tk.Canvas(shell,bg=BG,highlightthickness=0);scroll=ttk.Scrollbar(shell,orient='vertical',command=canvas.yview);canvas.configure(yscrollcommand=scroll.set);scroll.pack(side='right',fill='y');canvas.pack(side='left',fill='both',expand=True);area=tk.Frame(canvas,bg=BG);window=canvas.create_window((0,0),window=area,anchor='nw');area.bind('<Configure>',lambda _e:canvas.configure(scrollregion=canvas.bbox('all')));canvas.bind('<Configure>',lambda e:canvas.itemconfigure(window,width=e.width));canvas.bind('<MouseWheel>',lambda e:canvas.yview_scroll(int(-e.delta/120),'units'));self.page=area
        route={'Mock Interview':'mock_interview','Candidate Screening':'candidate_screening'}
        handler=getattr(self,'page_'+route.get(page,page.lower().replace(' ','_').replace('/','_')),None)
        (handler or self.page_dashboard)()
    def logout(self): self.user=None; self.show_auth()
    def section(self,title,sub=''):
        self.label(self.page,title,18,True,bg=BG).pack(anchor='w',pady=(4,3))
        if sub:self.label(self.page,sub,10,False,MUTED,bg=BG).pack(anchor='w',pady=(0,12))
    def cards(self,values):
        row=tk.Frame(self.page,bg=BG); row.pack(fill='x',pady=12)
        for title,value,caption in values:
            f=tk.Frame(row,bg=CARD,padx=18,pady=15,highlightbackground='#e6e7ef',highlightthickness=1); f.pack(side='left',fill='both',expand=True,padx=(0,12)); self.label(f,title,10,True,MUTED,bg=CARD).pack(anchor='w'); self.label(f,str(value),26,True,PURPLE,bg=CARD).pack(anchor='w',pady=4); self.label(f,caption,9,False,MUTED,bg=CARD).pack(anchor='w')
    def tree(self,parent,cols,rows):
        style=ttk.Style(self);style.configure('Treeview',background=CARD,fieldbackground=CARD,foreground=INK,rowheight=28);style.configure('Treeview.Heading',background='#e9e8fb' if not DARK else '#303149',foreground=INK,font=('Segoe UI',9,'bold'));style.map('Treeview',background=[('selected',PURPLE)],foreground=[('selected','white')])
        box=tk.Frame(parent,bg=CARD); box.pack(fill='both',expand=True,pady=10); t=ttk.Treeview(box,columns=cols,show='headings',height=13)
        for c in cols:t.heading(c,text=c);t.column(c,width=max(100,850//len(cols)),anchor='w')
        for r in rows:t.insert('','end',values=tuple(r))
        sb=ttk.Scrollbar(box,orient='vertical',command=t.yview);t.configure(yscrollcommand=sb.set);t.pack(side='left',fill='both',expand=True);sb.pack(side='right',fill='y');return t
    def page_dashboard(self):
        if self.user['role']=='applicant':
            with connect() as c:
                apps=c.execute('SELECT COUNT(*) FROM Applications WHERE applicant_id=?',(self.user['id'],)).fetchone()[0]; shortlisted=c.execute("SELECT COUNT(*) FROM Applications WHERE applicant_id=? AND status IN ('Shortlisted','Interview')",(self.user['id'],)).fetchone()[0]; resumes=c.execute('SELECT score FROM Resumes WHERE user_id=? ORDER BY id DESC LIMIT 1',(self.user['id'],)).fetchone(); jobs=c.execute("SELECT COUNT(*) FROM Jobs WHERE status='Open'").fetchone()[0]; upcoming=c.execute("SELECT COUNT(*) FROM Interviews i JOIN Applications a ON a.id=i.application_id WHERE a.applicant_id=? AND i.scheduled_at>=datetime('now')",(self.user['id'],)).fetchone()[0]; recent=c.execute('SELECT j.title,c.name,a.status FROM Applications a JOIN Jobs j ON j.id=a.job_id JOIN Companies c ON c.id=j.company_id WHERE a.applicant_id=? ORDER BY a.created_at DESC LIMIT 5',(self.user['id'],)).fetchall(); recommended=c.execute("SELECT j.*,c.name company FROM Jobs j JOIN Companies c ON c.id=j.company_id WHERE j.status='Open'").fetchall(); latest_resume=c.execute('SELECT * FROM Resumes WHERE user_id=? ORDER BY id DESC LIMIT 1',(self.user['id'],)).fetchone()
            recommended=sorted(recommended,key=lambda item:score_resume(dict(latest_resume) if latest_resume else {},dict(item))['score'],reverse=True)[:3]
            self.section('Good to see you, '+self.user['name'].split()[0],'Your next opportunity is closer than you think.')
            self.cards([('Applications',apps,'Submitted so far'),('Shortlisted',shortlisted,'Moving forward'),('Upcoming interviews',upcoming,'Scheduled conversations'),('Resume readiness',str(resumes[0])+'%' if resumes else '—','Upload your resume to score')])
            self.section('Recommended jobs',f'{jobs} openings currently available')
            if recommended:self.tree(self.page,['Role','Company','Location','Match'],[(r['title'],r['company'],r['location'],str(score_resume(dict(latest_resume) if latest_resume else {},dict(r))['score'])+'%') for r in recommended])
            else:self.label(self.page,'No open roles yet. Check back as employers post jobs.',10,False,MUTED,bg=BG).pack(anchor='w',pady=8)
            self.section('Recent application activity')
            if recent:self.tree(self.page,['Job','Company','Status'],[tuple(r) for r in recent])
            else:self.label(self.page,'Your applications will appear here after you apply to a role.',10,False,MUTED,bg=BG).pack(anchor='w',pady=8)
            self.section('Get started','Make progress on your career journey')
            for text,cmd in [('Browse open jobs',lambda:self.show_app('Find Jobs')),('Analyze your resume',lambda:self.show_app('Resume Analyzer')),('Build a career roadmap',lambda:self.show_app('Career Guidance'))]: self.button(self.page,text,cmd).pack(side='left',padx=(0,10),pady=6)
        else:
            with connect() as c:
                co=c.execute('SELECT id FROM Companies WHERE user_id=?',(self.user['id'],)).fetchone(); jobs=c.execute('SELECT COUNT(*) FROM Jobs WHERE company_id=? AND status="Open"',(co['id'],)).fetchone()[0]; apps=c.execute('SELECT COUNT(*) FROM Applications a JOIN Jobs j ON j.id=a.job_id WHERE j.company_id=?',(co['id'],)).fetchone()[0]; shortlisted=c.execute("SELECT COUNT(*) FROM Applications a JOIN Jobs j ON j.id=a.job_id WHERE j.company_id=? AND a.status IN ('Shortlisted','Interview')",(co['id'],)).fetchone()[0]; upcoming=c.execute("SELECT COUNT(*) FROM Interviews i JOIN Applications a ON a.id=i.application_id JOIN Jobs j ON j.id=a.job_id WHERE j.company_id=? AND i.scheduled_at>=datetime('now')",(co['id'],)).fetchone()[0]
            self.section('Recruiter overview','Your hiring activity at a glance'); self.cards([('Active openings',jobs,'Roles accepting applicants'),('Applications',apps,'Across your openings'),('Shortlisted',shortlisted,'Candidates to follow up'),('Upcoming interviews',upcoming,'Scheduled conversations')]); self.section('Recent applicants')
            with connect() as c: rows=c.execute('SELECT u.name,j.title,a.status,a.match_score,a.created_at FROM Applications a JOIN Users u ON u.id=a.applicant_id JOIN Jobs j ON j.id=a.job_id WHERE j.company_id=? ORDER BY a.created_at DESC LIMIT 8',(co['id'],)).fetchall()
            self.tree(self.page,['Candidate','Job','Status','Match','Applied'],[tuple(r) for r in rows])
    def page_find_jobs(self):
        self.section('Discover opportunities','Search live openings posted by HireSphere employers')
        bar=tk.Frame(self.page,bg=BG); bar.pack(fill='x',pady=8); self.search=self.entry(bar,'Title or company');self.search.pack(side='left',fill='x',expand=True,padx=(0,8)); self.loc=self.entry(bar,'Location');self.loc.pack(side='left',fill='x',expand=True,padx=8); self.kind=ttk.Combobox(bar,values=['Any','Full-time','Part-time','Contract','Internship'],state='readonly',width=13);self.kind.set('Any');self.kind.pack(side='left',padx=8); self.button(bar,'Search',self.load_jobs,True).pack(side='left',padx=8); self.jobbox=tk.Frame(self.page,bg=BG);self.jobbox.pack(fill='both',expand=True);self.load_jobs()
    def load_jobs(self):
        for w in self.jobbox.winfo_children():w.destroy()
        try: rows=job_service.jobs(self.search.get(),self.loc.get(),self.kind.get())
        except: rows=job_service.jobs()
        for j in rows:
            f=tk.Frame(self.jobbox,bg=CARD,padx=18,pady=14,highlightbackground='#e5e6ee',highlightthickness=1); f.pack(fill='x',pady=6); self.label(f,j['title'],15,True,bg=CARD).grid(row=0,column=0,sticky='w'); self.label(f,j['company']+'  ·  '+(j['location'] or 'Location flexible')+'  ·  '+j['job_type'],10,False,MUTED,bg=CARD).grid(row=1,column=0,sticky='w',pady=4); self.label(f,'Skills: '+(j['required_skills'] or 'Not specified')+'    Salary: '+(j['salary'] or 'Not specified'),9,False,MUTED,bg=CARD).grid(row=2,column=0,sticky='w'); self.label(f,j['description'][:230],10,False,INK,bg=CARD,wraplength=730,justify='left').grid(row=3,column=0,sticky='w',pady=8); actions=tk.Frame(f,bg=CARD);actions.grid(row=0,column=1,rowspan=2,padx=12);self.button(actions,'Apply',lambda jid=j['id']:self.apply_job(jid),True).pack(pady=3);self.button(actions,'Save job',lambda jid=j['id']:self.save_job_for_later(jid)).pack(pady=3)
    def save_job_for_later(self,jid):
        try:
            with connect() as c:c.execute('INSERT OR IGNORE INTO SavedJobs(user_id,job_id) VALUES(?,?)',(self.user['id'],jid))
            messagebox.showinfo('Saved','Job saved to your account.')
        except Exception as e:messagebox.showerror('Saved jobs',str(e))
    def page_saved_jobs(self):
        self.section('Saved jobs','Open roles you saved for later')
        with connect() as c:rows=c.execute('SELECT j.id,j.title,c.name,j.location,j.job_type,j.salary FROM SavedJobs s JOIN Jobs j ON j.id=s.job_id JOIN Companies c ON c.id=j.company_id WHERE s.user_id=? ORDER BY s.created_at DESC',(self.user['id'],)).fetchall()
        self.saved_tree=self.tree(self.page,['ID','Job','Company','Location','Type','Salary'],[tuple(r) for r in rows]);bar=tk.Frame(self.page,bg=BG);bar.pack(anchor='w');self.button(bar,'Apply',self.apply_saved,True).pack(side='left',padx=4);self.button(bar,'Remove saved job',self.remove_saved).pack(side='left',padx=4)
    def selected_saved_job(self):
        selected=self.saved_tree.selection()
        if not selected:messagebox.showinfo('Saved jobs','Select a saved job first.');return None
        return self.saved_tree.item(selected[0])['values'][0]
    def apply_saved(self):
        jid=self.selected_saved_job()
        if jid is not None:self.apply_job(jid)
    def remove_saved(self):
        jid=self.selected_saved_job()
        if jid is not None:
            with connect() as c:c.execute('DELETE FROM SavedJobs WHERE user_id=? AND job_id=?',(self.user['id'],jid))
            self.show_app('Saved Jobs')
    def apply_job(self,jid):
        try: m=application_service.apply(self.user['id'],jid); messagebox.showinfo('Application submitted',f"Application sent. Resume match: {m['score']}%\nMatching: {', '.join(m['matching']) or 'None found'}\nMissing: {', '.join(m['missing']) or 'None'}")
        except Exception as e: messagebox.showerror('Application','You have already applied to this opening.' if 'UNIQUE constraint failed' in str(e) else str(e))
    def page_my_applications(self): self.applications_table(self.user['id'])
    def page_applications(self): self.page_recruiter_applications()
    def applications_table(self,user_id=None):
        if user_id:
            with connect() as c: rows=c.execute('SELECT a.id,c.name,j.title,a.created_at,a.match_score,a.status,a.matching_skills,a.missing_skills FROM Applications a JOIN Jobs j ON j.id=a.job_id JOIN Companies c ON c.id=j.company_id WHERE a.applicant_id=? ORDER BY a.created_at DESC',(user_id,)).fetchall()
            self.section('Your applications','Status updates from each hiring team');self.tree(self.page,['ID','Company','Job','Applied','Match %','Status','Matching skills','Missing skills'],[tuple(r) for r in rows])
        else: self.page_recruiter_applications()
    def page_recruiter_applications(self):
        self.section('Candidate applications','Review candidates and make the hiring decision')
        with connect() as c:
            co=c.execute('SELECT id FROM Companies WHERE user_id=?',(self.user['id'],)).fetchone(); rows=c.execute('SELECT a.id,u.name,j.title,a.created_at,a.match_score,a.status,a.matching_skills,a.missing_skills,a.applicant_id,a.resume_id FROM Applications a JOIN Users u ON u.id=a.applicant_id JOIN Jobs j ON j.id=a.job_id WHERE j.company_id=? ORDER BY a.created_at DESC',(co['id'],)).fetchall()
        self.app_rows=rows; self.app_tree=self.tree(self.page,['ID','Candidate','Job','Applied','Match %','Status','Matching skills','Missing skills'],[tuple(r[:8]) for r in rows]); bar=tk.Frame(self.page,bg=BG);bar.pack(anchor='w'); self.button(bar,'Update status',self.update_status,True).pack(side='left',padx=4);self.button(bar,'Candidate profile',self.view_candidate_profile).pack(side='left',padx=4);self.button(bar,'View resume',self.view_resume).pack(side='left',padx=4);self.button(bar,'Schedule interview',self.schedule_interview).pack(side='left',padx=4)
    def selected_application(self):
        sel=self.app_tree.selection()
        if not sel: messagebox.showinfo('Select application','Choose an application row first.'); return None
        return next((r for r in self.app_rows if str(r['id'])==str(self.app_tree.item(sel[0])['values'][0])),None)
    def update_status(self):
        row=self.selected_application()
        if row:
            status=simpledialog.askstring('Application status','Enter: Applied, Under Review, Shortlisted, Interview, Selected or Rejected',initialvalue=row['status'])
            if status:
                valid=['Applied','Under Review','Shortlisted','Interview','Selected','Rejected']
                if status.title() not in valid: messagebox.showerror('Invalid status','Choose one of: '+', '.join(valid));return
                with connect() as c:c.execute('UPDATE Applications SET status=? WHERE id=?',(status.title(),row['id']))
                self.show_app('Applications')
    def view_resume(self):
        row=self.selected_application()
        if row:
            with connect() as c:r=c.execute('SELECT filename,text FROM Resumes WHERE id=?',(row['resume_id'],)).fetchone()
            if not r: messagebox.showinfo('Resume','This candidate has not uploaded a resume.');return
            win=tk.Toplevel(self);win.title(r['filename']);win.geometry('700x560');t=tk.Text(win,wrap='word',bg=CARD,fg=INK);t.pack(fill='both',expand=True);t.insert('1.0',r['text']);t.configure(state='disabled')
    def view_candidate_profile(self):
        row=self.selected_application()
        if not row:return
        with connect() as c:
            user=c.execute('SELECT u.name,u.email,p.phone,p.location,p.skills,p.target_role FROM Users u LEFT JOIN ApplicantProfiles p ON p.user_id=u.id WHERE u.id=?',(row['applicant_id'],)).fetchone()
            resume=c.execute('SELECT * FROM Resumes WHERE id=?',(row['resume_id'],)).fetchone() if row['resume_id'] else None
            job=c.execute('SELECT j.* FROM Jobs j JOIN Applications a ON a.job_id=j.id WHERE a.id=?',(row['id'],)).fetchone()
        scoring=score_resume(dict(resume) if resume else {},dict(job))
        content=f"Candidate: {user['name']}\nEmail: {user['email']}\nPhone: {user['phone'] or 'Not provided'}\nLocation: {user['location'] or 'Not provided'}\nTarget role: {user['target_role'] or 'Not provided'}\nProfile skills: {user['skills'] or 'Not provided'}\n\nMatch score: {scoring['score']}%\nBreakdown: {scoring['breakdown']}\nMatching skills: {', '.join(scoring['matching']) or 'None found'}\nMissing skills: {', '.join(scoring['missing']) or 'None'}\nRelevant project text: {scoring['relevant_projects'] or 'No relevant project text detected'}\n\nResume education: {resume['education'] if resume else 'No resume uploaded'}\nResume experience: {resume['experience'] if resume else 'No resume uploaded'}\nCertifications: {resume['certifications'] if resume else 'No resume uploaded'}\n\nScoring is a transparent heuristic. Hiring decisions remain with the recruiter."
        win=tk.Toplevel(self);win.title('Candidate profile and match');win.geometry('700x560');t=tk.Text(win,wrap='word',bg=CARD,fg=INK);t.pack(fill='both',expand=True);t.insert('1.0',content);t.configure(state='disabled')
    def schedule_interview(self):
        row=self.selected_application()
        if row:
            when=simpledialog.askstring('Schedule interview','Date/time (YYYY-MM-DD HH:MM)')
            if when:
                try:scheduled=datetime.strptime(when.strip(),'%Y-%m-%d %H:%M').isoformat(sep=' ')
                except ValueError:messagebox.showerror('Interview date','Enter the date and time as YYYY-MM-DD HH:MM.');return
                notes=simpledialog.askstring('Interview notes','Optional location or meeting details') or ''
                with connect() as c:c.execute('INSERT INTO Interviews(application_id,scheduled_at,interview_type,notes) VALUES(?,?,?,?)',(row['id'],scheduled,'Interview',notes));c.execute("UPDATE Applications SET status='Interview' WHERE id=?",(row['id'],))
                messagebox.showinfo('Interview','Interview scheduled and saved. Application status updated to Interview.')
    def page_post_a_job(self): self.job_form()
    def job_form(self,job=None):
        self.section('Create a job opening','Add clear requirements to help candidates find the right opportunity')
        fields=[('title','Job title'),('description','Description'),('required_skills','Required skills (comma separated)'),('preferred_skills','Preferred skills'),('experience','Experience requirements'),('salary','Salary range'),('location','Location'),('job_type','Job type')]; self.job_inputs={};self.editing_job=job['id'] if job else None
        for key,hint in fields:
            self.label(self.page,hint,10,True,MUTED,bg=BG).pack(anchor='w',pady=(5,2))
            e=tk.Text(self.page,height=5,wrap='word',bg=CARD,fg=INK,insertbackground=INK,relief='solid',bd=1) if key=='description' else self.entry(self.page,hint)
            e.pack(fill='x',pady=(0,2));self.job_inputs[key]=e
            if job and key in job.keys():e.insert('1.0' if key=='description' else 0,job[key] or '')
        self.button(self.page,'Save changes' if job else 'Publish opening',self.save_job,True).pack(anchor='w',pady=14)
    def save_job(self):
        try:
            data={key:(widget.get('1.0','end').strip() if isinstance(widget,tk.Text) else widget.get().strip()) for key,widget in self.job_inputs.items()}
            job_service.create_job(self.user['id'],data,self.editing_job);messagebox.showinfo('Job posted','Your opening is now visible to applicants.');self.show_app('Manage Jobs')
        except Exception as e:messagebox.showerror('Job posting',str(e))
    def page_manage_jobs(self):
        self.section('Manage openings','Edit your roles or close positions that are filled')
        with connect() as c:co=c.execute('SELECT id FROM Companies WHERE user_id=?',(self.user['id'],)).fetchone();rows=c.execute('SELECT id,title,location,job_type,status,created_at FROM Jobs WHERE company_id=? ORDER BY id DESC',(co['id'],)).fetchall()
        t=self.tree(self.page,['ID','Job title','Location','Type','Status','Created'],[tuple(r) for r in rows]); row=tk.Frame(self.page,bg=BG);row.pack(anchor='w');self.button(row,'Edit selected job',lambda:self.edit_job(t,rows)).pack(side='left',padx=4);self.button(row,'Close selected job',lambda:self.close_job(t),True).pack(side='left',padx=4)
    def edit_job(self,t,rows):
        sel=t.selection()
        if not sel:messagebox.showinfo('Select a job','Choose a job row first.');return
        jid=t.item(sel[0])['values'][0];job=next(r for r in rows if r['id']==jid)
        self.show_app('Post a Job')
        for widget in self.page.winfo_children():widget.destroy()
        self.job_form(job)
    def close_job(self,t):
        sel=t.selection()
        if sel:
            jid=t.item(sel[0])['values'][0]
            if not messagebox.askyesno('Close job','Close this opening? Applicants will no longer see it.'):
                return
            with connect() as c:c.execute("UPDATE Jobs SET status='Closed' WHERE id=?",(jid,))
            self.show_app('Manage Jobs')
    def page_resume_analyzer(self):
        self.section('Resume analyzer','Extract information from your PDF and see an honest completeness estimate')
        self.label(self.page,'The analyzer reads selectable PDF text; scanned image-only PDFs need OCR. Extracted sections are shown as found, without invented content.',10,False,MUTED,bg=BG,wraplength=800,justify='left').pack(anchor='w',pady=8);self.button(self.page,'Choose PDF resume',self.upload_resume,True).pack(anchor='w',pady=10);self.resume_result=tk.Text(self.page,height=20,wrap='word',font=('Segoe UI',10),relief='flat',bg=CARD,fg=INK);self.resume_result.pack(fill='both',expand=True,pady=8)
        with connect() as c:r=c.execute('SELECT filename,score,skills FROM Resumes WHERE user_id=? ORDER BY id DESC LIMIT 1',(self.user['id'],)).fetchone()
        if r:self.resume_result.insert('end',f"Latest saved resume: {r['filename']}\nCompleteness: {r['score']}%\nSkills: {r['skills']}\n")
    def upload_resume(self):
        path=filedialog.askopenfilename(filetypes=[('PDF files','*.pdf')])
        if not path:return
        self.resume_result.delete('1.0','end');self.resume_result.insert('end','Extracting PDF text…')
        def work():
            try:
                result=parse_pdf(path)
                with connect() as c:c.execute('INSERT INTO Resumes(user_id,filename,text,skills,education,projects,experience,certifications,score) VALUES(?,?,?,?,?,?,?,?,?)',(self.user['id'],result['filename'],result['text'],result['skills'],result['education'],result['projects'],result['experience'],result['certifications'],result['score']));c.execute('UPDATE ApplicantProfiles SET skills=? WHERE user_id=?',(result['skills'],self.user['id']))
                self.after(0,lambda:self.display_resume(result))
            except Exception as e:self.after(0,lambda:messagebox.showerror('Resume analysis',str(e)))
        threading.Thread(target=work,daemon=True).start()
    def display_resume(self,r):
        self.resume_result.delete('1.0','end');self.resume_result.insert('end',f"{r['filename']}\nCompleteness score: {r['score']}%\n\nSkills found: {r['skills'] or 'None detected'}\n\nEducation: {r['education'] or 'No education heading found'}\n\nExperience: {r['experience'] or 'No experience heading found'}\n\nProjects: {r['projects'] or 'No projects heading found'}\n\nCertifications: {r['certifications'] or 'No certifications heading found'}\n\nImprovement: add clear section headings and quantify project outcomes. Missing information is left blank.\n\nExtracted text preview\n{'-'*32}\n{r['text']}")
    def page_candidate_screening(self): self.page_recruiter_applications()
    def page_shortlisted_candidates(self):
        self.section('Shortlisted candidates','Candidates shortlisted by your hiring team')
        with connect() as c:co=c.execute('SELECT id FROM Companies WHERE user_id=?',(self.user['id'],)).fetchone();rows=c.execute("SELECT u.name,j.title,a.match_score,a.matching_skills,a.status FROM Applications a JOIN Users u ON u.id=a.applicant_id JOIN Jobs j ON j.id=a.job_id WHERE j.company_id=? AND a.status IN ('Shortlisted','Interview','Selected')",(co['id'],)).fetchall()
        self.tree(self.page,['Candidate','Job','Match %','Skills','Status'],[tuple(r) for r in rows])
    def page_interviews(self):
        self.section('Interviews','Scheduled conversations with candidates')
        query='SELECT i.id,u.name,j.title,i.scheduled_at,i.interview_type,i.status,i.notes FROM Interviews i JOIN Applications a ON a.id=i.application_id JOIN Users u ON u.id=a.applicant_id JOIN Jobs j ON j.id=a.job_id'
        if self.user['role']=='recruiter':query+=' JOIN Companies c ON c.id=j.company_id WHERE c.user_id=?'; args=(self.user['id'],)
        else:query+=' WHERE a.applicant_id=?';args=(self.user['id'],)
        with connect() as c:rows=c.execute(query+' ORDER BY i.scheduled_at',args).fetchall()
        self.interview_rows=rows;self.interview_tree=self.tree(self.page,['ID','Candidate','Job','Date / time','Type','Status','Details'],[tuple(r) for r in rows])
        if self.user['role']=='recruiter':self.button(self.page,'Update interview status or notes',self.update_interview_details,True).pack(anchor='w')
    def update_interview_details(self):
        selected=self.interview_tree.selection()
        if not selected:messagebox.showinfo('Select interview','Choose an interview first.');return
        iid=self.interview_tree.item(selected[0])['values'][0];row=next(r for r in self.interview_rows if r['id']==iid)
        status=simpledialog.askstring('Interview status','Enter Scheduled, Completed, or Cancelled',initialvalue=row['status'])
        if not status:return
        if status.title() not in ('Scheduled','Completed','Cancelled'):messagebox.showerror('Interview status','Choose Scheduled, Completed, or Cancelled.');return
        notes=simpledialog.askstring('Interview notes','Update interview details or notes',initialvalue=row['notes'] or '')
        with connect() as c:c.execute('UPDATE Interviews SET status=?,notes=? WHERE id=?',(status.title(),notes or '',iid))
        self.show_app('Interviews')
    def page_mock_interview(self):
        self.section('Mock interview','Practice offline with predefined questions and transparent keyword-based feedback')
        self.label(self.page,'Rule-based practice only. Answers are scored for coverage of interview topic keywords; no external AI service is used.',10,False,MUTED,bg=BG,wraplength=780,justify='left').pack(anchor='w',pady=8)
        self.interview_role=self.entry(self.page,'Target job role');self.interview_role.pack(fill='x',pady=5);self.interview_type=tk.StringVar(value='Technical')
        if ctk:ctk.CTkSegmentedButton(self.page,values=['Technical','HR','Behavioral'],variable=self.interview_type).pack(anchor='w',pady=8)
        else:ttk.Combobox(self.page,textvariable=self.interview_type,values=['Technical','HR','Behavioral'],state='readonly').pack(anchor='w',pady=8)
        self.difficulty=tk.StringVar(value='Intermediate');self.label(self.page,'Difficulty',10,True,MUTED,bg=BG).pack(anchor='w')
        if ctk:ctk.CTkSegmentedButton(self.page,values=['Beginner','Intermediate','Advanced'],variable=self.difficulty).pack(anchor='w',pady=6)
        else:ttk.Combobox(self.page,textvariable=self.difficulty,values=['Beginner','Intermediate','Advanced'],state='readonly').pack(anchor='w',pady=6)
        self.question=tk.StringVar(value='Choose your options, then start practice.');self.label(self.page,'Question',12,True,PURPLE,bg=BG).pack(anchor='w',pady=(12,4));self.question_display=self.label(self.page,self.question.get(),15,True,bg=BG,wraplength=760,justify='left');self.question_display.pack(anchor='w')
        self.answer=tk.Text(self.page,height=8,wrap='word',bg=CARD,fg=INK,insertbackground=INK);self.answer.pack(fill='x',pady=12);self.practice_button=self.button(self.page,'Start practice',self.start_interview,True);self.practice_button.pack(anchor='w');self.button(self.page,'Submit answer',self.evaluate_interview).pack(anchor='w',pady=8)
        self.q_index=-1;self.session_questions=[];self.session_results=[];self.active_question=None
    def start_interview(self):
        if self.session_questions and self.q_index >= len(self.session_questions)-1:
            self.show_interview_report();return
        if not self.session_questions:
            try:self.session_questions=interview_service.question_bank(self.interview_role.get(),self.interview_type.get(),self.difficulty.get())
            except Exception as e:messagebox.showerror('Mock interview',str(e));return
        self.q_index+=1;self.active_question=self.session_questions[self.q_index];self.question.set(self.active_question['question']);self.question_display.configure(text=self.question.get());self.answer.delete('1.0','end');self.practice_button.configure(text='Finish and view report' if self.q_index==len(self.session_questions)-1 else 'Next question')
    def evaluate_interview(self):
        if not self.active_question:messagebox.showinfo('Mock interview','Start practice to load a question first.');return
        answer=self.answer.get('1.0','end').strip()
        try:result=interview_service.evaluate_answer(self.active_question,answer)
        except Exception as e:messagebox.showinfo('Answer',str(e));return
        self.session_results.append(result)
        with connect() as c:c.execute('INSERT INTO InterviewResults(user_id,role,difficulty,interview_type,questions,answers,feedback,score) VALUES(?,?,?,?,?,?,?,?)',(self.user['id'],self.interview_role.get(),self.difficulty.get(),self.interview_type.get(),self.active_question['question'],answer,result['feedback'],result['score']))
        messagebox.showinfo('Rule-based feedback',f"Score: {result['score']}%\n{result['feedback']}")
    def show_interview_report(self):
        if not self.session_results:messagebox.showinfo('Mock interview','Submit at least one answer to create a report.');return
        average=round(sum(r['score'] for r in self.session_results)/len(self.session_results));summary='\n'.join(f"Question {i+1}: {r['score']}% — {r['feedback']}" for i,r in enumerate(self.session_results))
        report=f"Rule-based interview report\nRole: {self.interview_role.get() or 'Not specified'}\nType: {self.interview_type.get()} | Difficulty: {self.difficulty.get()}\nQuestions answered: {len(self.session_results)}\nOverall keyword coverage: {average}%\n\n{summary}\n\nThis score measures keyword coverage only. Use it as practice guidance, not as a hiring assessment."
        messagebox.showinfo('Interview report',report);self.question.set('Report complete. Start again to practice another set.');self.question_display.configure(text=self.question.get());self.session_questions=[];self.session_results=[];self.active_question=None;self.q_index=-1;self.practice_button.configure(text='Start practice')
    def page_career_guidance(self):
        self.section('Career guidance','Use your saved resume skills to map a practical next step');self.target=self.entry(self.page,'Target role (e.g. Data Analyst)');self.target.pack(fill='x',pady=6)
        with connect() as c:profile=c.execute('SELECT target_role FROM ApplicantProfiles WHERE user_id=?',(self.user['id'],)).fetchone()
        if profile and profile['target_role']:self.target.insert(0,profile['target_role'])
        self.button(self.page,'Build my roadmap',self.build_roadmap,True).pack(anchor='w',pady=6);self.guidance=tk.Text(self.page,height=22,wrap='word',font=('Segoe UI',11),bg=CARD,fg=INK,insertbackground=INK);self.guidance.pack(fill='both',expand=True,pady=8)
    def build_roadmap(self):
        with connect() as c:r=c.execute('SELECT skills FROM Resumes WHERE user_id=? ORDER BY id DESC LIMIT 1',(self.user['id'],)).fetchone()
        have=set(x.strip().lower() for x in (r['skills'] if r else '').split(',') if x.strip()); role=self.target.get().strip() or 'your target role'
        with connect() as c:c.execute('UPDATE ApplicantProfiles SET target_role=? WHERE user_id=?',(role,self.user['id']))
        with connect() as c: j=c.execute("SELECT required_skills FROM Jobs WHERE status='Open' AND title LIKE ? LIMIT 10",(f'%{role.split()[0]}%',)).fetchall()
        demand=set(x.strip().lower() for row in j for x in (row[0] or '').split(',') if x.strip()); gap=sorted(demand-have)
        readiness=round(100*len(have & demand)/max(len(demand),1)) if demand else (35 if have else 0)
        self.guidance.delete('1.0','end');self.guidance.insert('end',f"Target: {role}\nCareer readiness: {readiness}%\nCurrent resume skills: {', '.join(sorted(have)) or 'Upload a resume to personalize this plan.'}\nSkills found in matching live jobs: {', '.join(sorted(demand)) or 'No close job title match yet; explore job listings and required skills.'}\n\nRecommended skill gaps: {', '.join(gap) or 'No gaps detected from the available matching jobs.'}\n\nSuggested project: Build a small, documented project that uses {', '.join(gap[:2]) or 'your strongest role relevant skills'}; include a clear README and measurable outcome.\n\nRoadmap\n1. Choose one priority gap and complete a focused learning module.\n2. Practice it in a portfolio project over the next 2–3 weeks.\n3. Add the project and measurable results to your resume.\n4. Revisit live job requirements and apply to roles that fit.")
    def page_my_profile(self): self.profile_page(False)
    def page_company_profile(self): self.profile_page(True)
    def profile_page(self,company):
        self.section('Company profile' if company else 'My profile','Manage the information connected to your account')
        with connect() as c:
            if company:r=c.execute('SELECT name,description FROM Companies WHERE user_id=?',(self.user['id'],)).fetchone()
            else:r=c.execute('SELECT phone,location,skills,target_role FROM ApplicantProfiles WHERE user_id=?',(self.user['id'],)).fetchone()
        self.profile_inputs={}
        fields=[('name','Company name'),('description','About the company')] if company else [('phone','Phone'),('location','Location'),('skills','Skills'),('target_role','Target role')]
        for key,hint in fields:
            self.label(self.page,hint,10,True,MUTED,bg=BG).pack(anchor='w',pady=(8,3));e=self.entry(self.page,hint);e.pack(fill='x');self.profile_inputs[key]=e
            if r and key in r.keys():e.insert(0,r[key] or '')
        self.button(self.page,'Save profile',lambda:self.save_profile(company),True).pack(anchor='w',pady=14)
    def save_profile(self,company):
        try:
            if company and not self.profile_inputs['name'].get().strip():raise ValueError('Company name is required.')
            with connect() as c:
                if company:c.execute('UPDATE Companies SET name=?,description=? WHERE user_id=?',(self.profile_inputs['name'].get(),self.profile_inputs['description'].get(),self.user['id']))
                else:c.execute('UPDATE ApplicantProfiles SET phone=?,location=?,skills=?,target_role=? WHERE user_id=?',(*(self.profile_inputs[k].get() for k in ('phone','location','skills','target_role')),self.user['id']))
            messagebox.showinfo('Profile','Profile saved.')
        except Exception as e:messagebox.showerror('Profile',str(e))
    def page_settings(self):
        self.section('Settings','Appearance and session');self.label(self.page,'Theme',11,True,MUTED,bg=BG).pack(anchor='w',pady=5)
        mode=tk.StringVar(value='Dark' if DARK else 'Light')
        if ctk:
            ctk.CTkSegmentedButton(self.page,values=['Light','Dark'],variable=mode,command=self.change_theme).pack(anchor='w')
        else:
            selector=ttk.Combobox(self.page,values=['Light','Dark'],textvariable=mode,state='readonly');selector.pack(anchor='w');selector.bind('<<ComboboxSelected>>',lambda _event:self.change_theme(mode.get()))
        self.button(self.page,'Log out',self.logout,True).pack(anchor='w',pady=20)
    def change_theme(self,mode):
        global BG,INK,MUTED,PURPLE,CARD,DARK
        DARK=mode=='Dark'
        if DARK:BG,INK,MUTED,PURPLE,CARD='#171821','#f2f2fa','#a5a8ba','#8176ff','#252633'
        else:BG,INK,MUTED,PURPLE,CARD='#f5f6fb','#1c2040','#777d95','#6258d9','#ffffff'
        if ctk:ctk.set_appearance_mode('dark' if DARK else 'light')
        self.show_app('Settings')
    def page_analytics(self):
        self.section('Hiring analytics','Application stage counts for your openings')
        with connect() as c:co=c.execute('SELECT id FROM Companies WHERE user_id=?',(self.user['id'],)).fetchone(); rows=c.execute('SELECT status,COUNT(*) n FROM Applications a JOIN Jobs j ON j.id=a.job_id WHERE j.company_id=? GROUP BY status',(co['id'],)).fetchall();per_job=c.execute('SELECT j.title,COUNT(a.id) n FROM Jobs j LEFT JOIN Applications a ON a.job_id=j.id WHERE j.company_id=? GROUP BY j.id ORDER BY n DESC LIMIT 8',(co['id'],)).fetchall()
        self.cards([(r['status'],r['n'],'Applications') for r in rows] or [('No data',0,'Applications will appear here')])
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            fig=Figure(figsize=(9,4),dpi=100);status_ax=fig.add_subplot(121);status_ax.bar([r['status'] for r in rows],[r['n'] for r in rows],color=PURPLE);status_ax.set_ylabel('Candidates');status_ax.set_title('Application stages');status_ax.tick_params(axis='x',rotation=35);job_ax=fig.add_subplot(122);job_ax.barh([r['title'][:22] for r in reversed(per_job)],[r['n'] for r in reversed(per_job)],color='#887ff0');job_ax.set_xlabel('Applications');job_ax.set_title('Applications per job');fig.tight_layout();canvas=FigureCanvasTkAgg(fig,master=self.page);canvas.draw();canvas.get_tk_widget().pack(fill='both',expand=True)
        except Exception as e:self.label(self.page,'Chart unavailable: '+str(e),10,False,MUTED,bg=BG).pack(anchor='w')

if __name__ == '__main__':
    database.init_db();app=HireSphere();app.mainloop()
