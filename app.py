# ----- CONFIGURE YOUR EDITOR TO USE 4 SPACES PER TAB ----- #
import pymysql as db
import settings
import sys

def connection():
    ''' User this function to create your connections '''
    con = db.connect(
        settings.mysql_host, 
        settings.mysql_user, 
        settings.mysql_passwd, 
        settings.mysql_schema)
    
    return con


def updateRank(rank1, rank2, movieTitle):

    # Create a new connection
    con=connection()

    # Create a cursor on the connection
    cur=con.cursor()

    try:
        float(rank1)
    except ValueError:
        return [("status",),("error",),]
    try:
        float(rank2)
    except ValueError:
        return [("status",),("error",),]

    if float(rank1)<0.0 or float(rank1)>10.0: #an einai ektos oriwn to rank1 pou dwsame
        return [("status",),("error",),]

    if float(rank2)<0.0 or float(rank2)>10.0: #antistoixa to rank2
        return [("status",),("error",),]
    
    plithos=cur.execute("""SELECT rank 
                            from movie 
                            where title=%s""",[movieTitle,]) #plithos tainiwn pou vrike me ton titlo movieTitle
    row=cur.fetchall()
     
    if plithos==1:
        (rank,)=row[0]
        print(rank)
        if rank==(None,): #an den yparxei katholou rank,diladi einai null/none
            average=(float(rank1)+float(rank2))/2.0  #vriskei mo me tis 2 nees times
        else:
            average=(float(rank1)+float(rank2)) #vriskei mo me tis 3 times
            average=(average+rank)/3.0      
        try:
            cur.execute("""UPDATE movie
                            et rank=%s 
                            where title=%s""",(float(average),movieTitle)) #kanw update sti vasi
            con.commit() #to apothikeuw sti vasi
        except:
            con.rollback() #alliws to anairw
        print (rank1, rank2, movieTitle)
        return [("status",),("ok",),]
    else:
        return [("status",),("error",),]   

   
def colleaguesOfColleagues(actorId1, actorId2):

    # Create a new connection
    con=connection()
    
    # Create a cursor on the connection
    cur=con.cursor()
   

    cur.execute("""CREATE TEMPORARY TABLE movies_1 
                SELECT movie_id 
                from role 
                where actor_id=%s""",[actorId1,]) # tainies pou xei paiksei o actorid1
    
    cur.execute("""CREATE TEMPORARY TABLE movies_2 
                    SELECT movie_id 
                    from role 
                    where actor_id=%s""",[actorId2,]) #tainies pou exei paiksei o actorid2
   
    cur.execute("""CREATE TEMPORARY TABLE potential_c 
                    SELECT actor_id 
                    from role r,movies_1 m 
                    where r.movie_id=m.movie_id and r.actor_id!=(%s)""",[actorId1,]) #oi ithopoioi pou exoun paiksei stis idies tainies me ton actorid1
   
    cur.execute("""CREATE TEMPORARY TABLE potential_d 
                    SELECT actor_id 
                    from role r,movies_2 m 
                    where r.movie_id=m.movie_id and r.actor_id!=(%s)""",[actorId2,]) #oi ithopoioi pou exoun paiksei stis idies tainies me ton actorid2
  
    cur.execute("""SELECT distinct r1.movie_id,pc.actor_id as c, pd.actor_id as d 
                    from role r1,role r2,actor a1,actor a2,potential_c pc,potential_d pd 
                    where pc.actor_id!=pd.actor_id and r1.actor_id=pc.actor_id and r2.actor_id=pd.actor_id 
                    and r1.movie_id=r2.movie_id and a1.actor_id=%s and a2.actor_id=%s""",(actorId1,actorId2))
   
    answer=cur.fetchall()
  
    mylist=list(answer) #metatropi se lista
    for i in range(0,len(mylist)):
        mylist[i]=list(mylist[i])
        mylist[i].append(actorId1)
        mylist[i].append(actorId2)


    result= [("movieTitle", "colleagueOfActor1", "colleagueOfActor2" ,"actor1","actor2"),]
    result.extend(mylist)

    return result


     
def actorPairs(actorId):

    # Create a new connection
    con=connection()
    
    # Create a cursor on the connection
    cur=con.cursor()

    sum=cur.execute("""CREATE temporary table unwanted_genres 
                        SELECT genre_id 
                        from movie_has_genre m,role r 
                        where m.movie_id=r.movie_id and r.actor_id=%s""",[actorId,]);#ayta einai ta eidi pou exei paiksei o actorId k synepws de theloume 

    a=7-int(sum) #gia na einai synolika toulaxiston 7 ta eidi tou actorId mazi me ton allo

    cur.execute("""CREATE temporary table unwanted_movies  
                    select movie_id,m.genre_id              
                    from movie_has_genre m,unwanted_genres g 
                    where m.genre_id=g.genre_id""")    #vriskei oles tis tainies twn eidwn pou de theloume,diladi oles tis tainies stis opoies prepei na min paizei o actor pou psaxnoume
    cur.execute("""CREATE temporary table unwanted_actors 
                    select distinct r.actor_id,m.movie_id   
                    from role r,unwanted_movies m           
                    where r.movie_id=m.movie_id""")#vriskoume olous tous ithopoious pou paizoun stis parapanw tainies,diladi olous tous ithopoious pou aporriptontai 
    cur.execute("""CREATE temporary table wanted_actors 
                    select actor_id                         
                    from actor a                            
                    where not exists(select actor_id 
                                    from unwanted_actors u 
                                    where a.actor_id=u.actor_id)""")# vriskei poioi einai telika oi ithopoioi pou den exoun paiksei sta eidi tou actorId,diladi oloi ektos ap tous unwanted pou eidame parapanw
    cur.execute("""SELECT w.actor_id                                            
                    from wanted_actors w,movie_has_genre m,role r               
                    where w.actor_id=r.actor_id and m.movie_id=r.movie_id 
                    group by w.actor_id 
                    having count(distinct m.genre_id)>=%s""",a) #telos edw,vriskoume poioi ap tous wanted ithopoious pou pirame akrivws apo panw, exoun arketa diaforetika eidi tainiwn wste na exoun athroisma 7 mazi me tou actorId
    rows=cur.fetchall()

    myl=list(rows)  #metatropi listas
    for i in range(0,len(myl)):
        myl[i]=list(myl[i])

    print (actorId)
    
    result=[("actor2Id",)]
    result.extend(myl)
    return result

def selectTopNactors(n):

    # Create a new connection
    con=connection()
    
    # Create a cursor on the connection
    cur=con.cursor()
    
    cur.execute("SELECT genre_name from genre") #pairnw ola ta onomata twn eidwn
    rows=cur.fetchall()
  
    mylist=list(rows) #ftiaxnw ti synoliki lista
    for i in range(0,len(mylist)):  #pairnw gia kathe eidos ksexwrista
        cur.execute("""SELECT genre_name,actor_id,count(distinct r.movie_id) as countM 
                        from genre g,role r,movie_has_genre mg 
                        where mg.movie_id=r.movie_id and mg.genre_id=g.genre_id and genre_name=%s 
                        group by genre_name,actor_id 
                        order by countM DESC           
                        LIMIT %s """,(rows[i],int(n))) #exw order by wste na vgazei to megalytero count panw panw gia kathe eidos,kai me to limit krataei mono osa einai to n
        result=cur.fetchall()
        l=list(result)
        for j in range(0,len(l)): #ftiaxnei lista gia to sygkekrimeno eidos 
            l[j]=list(l[j])
        if i==0:        
            mylist=l  #an einai sto prwto loop
        else:                       #enwnei ti lista sti synoliki lista        
            mylist.extend(l)   
         
     
    print(mylist)
    result= [("genreName", "actorId", "numberOfMovies"),]
    result.extend(mylist)
    return result

