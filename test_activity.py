import mysql.connector
from transitions import Machine
import sys
query=("SELECT * FROM sensor_readings where time_stamp > '2017-11-05 00:00:00' order by time_stamp asc");
connector=mysql.connector.connect(host='localhost',port='3306', user='root',password='root',database='Sensors'); 
cursor=connector.cursor(); 
cursor.execute(query);
data=cursor.fetchall(); 
in_min = data[0][2].minute
i=0; 
cluster={};
list=[];
#print 'Start', in_min
for row in data:
	curr_min =row[2].minute;
	if curr_min is not in_min:
		#cluster[in_min]=list;
		cluster[str(in_hour)+str(in_min)]=list;
		in_min = row[2].minute
		#print '-------------------For Minute', in_min
		#cluster[curr_min].append(row[2]);
		#print row;
		#print list;
		#print cluster[str(in_min)];
		list=[];
		list.append(row);
	else:
		'''cluster[curr_min]=list;'''
		'''cluster[curr_min].append(row[2]);'''
		in_hour=row[2].hour;
		#print row;
		list.append(row);
#print row[2].minute;
#print type(data);
#print type(row);
#print cluster.keys();
#j=0;
'''for key,value in cluster.iteritems():
	print key,value;'''
events={};
final=[];
count=1;
for key in cluster.keys():
	transform=[];
	for j in cluster[key]:
		if ((str(j[0])=='d1') & (j[1]==1)):
			transform.append('d1_in');
			count=count+j[1];
		elif((str(j[0])=='d1') & (j[1]==-1)):
			transform.append('d1_out');
			count=count+j[1];
		elif((str(j[0])=='d2') & (j[1]==1)):
			transform.append('d2_in');
			count=count+j[1];
		elif((str(j[0])=='d2') & (j[1]==-1)):
			transform.append('d2_out');
			count=count+j[1];
		elif((str(j[0])=='r1') & (j[1]==1)):
			transform.append('r_open');
		elif((str(j[0])=='r1') & (j[1]==0)):
			transform.append('r_close');
		elif((str(j[0])=='u1') & (j[1] < 80)):
			transform.append('u_in');
		elif((str(j[0])=='u1') & (j[1] > 80)):
			transform.append('u_out');
		elif ((str(j[0])=='p1') & (j[1] == 1)):
			transform.append('p_m');
	events[key]=transform;
	final.append(transform);
	#print (transform);
	#print ('\n');
		
count=1;
p_flag=0;
u_flag=0;

for j in events.keys():
	#print j,events[j];
	pattern=events[j];
	p_flag=0;
	u_flag=0;
	#print 'activity in kitchen at'+str(j);
	for i in pattern:
		if (i=='d1_in'):
			count=count+1;
			#print 'someone came in, '+str(count)+' persons in kitchen;';
		elif (i=='d1_out'):
			count=count-1;
			if(count<0):
				count=0;
			#print 'someone went out, '+str(count)+' persons in kitchen;';
#			print '; ';
		elif (i=='d2_in'):
			count=count+1;
			#print 'someone came in, '+str(count)+' persons in kitchen;';
#			print '; ';
		elif (i=='d2_out'):
			count=count-1;
			if(count<0):
				count=0;
			#print 'someone went out, '+str(count)+' persons in kitchen;';
#			print '; ';
		elif ((i=='u_in') & (u_flag==0)):
			#print 'someone is using burner;';
			u_flag=1;
#			print '; ';
		elif (i=='r_open'):
			pass
			#print 'someone opened refrigerator;';
#			print '; ';
		elif (i=='r_close'):
			pass
			#print 'someone closed refrigerator;';
#			print '; ';
		elif ((i=='p_m') & (count>0) & (p_flag==0)):
			#print 'someone is moving in kitchen;';
#			print '; ';
			p_flag=1;
	#print '\n';
#print count;
cursor.close();
connector.close();

class activity:
	
        def __init__(self):
                self.current='';
                self.count=0;
                self.count_appearance=0;

	
	def door(self):
		if (self.current=='d1_in' or self.current=='d2_in'):
			self.count=self.count+1;
			if (self.count==1):
                                return True;
                        else:
                                return False;
		elif(self.current=='d1_out' or self.current=='d2_out'):
			self.count=self.count-1;
			if(self.count<=0):
                                self.count=0;
                                return True;
                        else:
                                return False;

	def move(self):
		if(self.current=='p_m'):
			return True;

	def gas(self):
		if(self.current=='u_in'):
			self.count_appearance+=1;
			if(self.count_appearance>=3):
                                self.count_appearance=0;
                                return True
                        else:
                                if(self.count_appearance==1):
                                        return True;
                                else:
                                        return False;
                        
        def refrigerator(self):
                if(self.current=='r_open'):
                        return True;
                elif(self.current=='r_close'):
                        return True;
        
        
a=activity();
states=['nothing','entered','appeared_near_burner','using_burner','using_refrigerator','used_refrigerator'];
machine=Machine(model=a,states=states,initial='nothing',ignore_invalid_triggers=True);
machine.add_transition('entry_exit','nothing','entered',conditions='door');
machine.add_transition('entry_exit','*','nothing',conditions='door');
machine.add_transition('using_g','entered','appeared_near_burner',conditions='gas');
machine.add_transition('using_r',['entered','appeared_near_burner','using_burner'],'using_refrigerator',conditions='refrigerator');
machine.add_transition('using_r','using_refrigerator','used_refrigerator',conditions='refrigerator');
machine.add_transition('using_g',['appeared_near_burner','using_refrigerator','used_refrigerator','using_burner'],'using_burner',conditions='gas');
machine.add_transition('enter','used_refrigerator','used_refrigerator',conditions='door');
machine.add_transition('enter','appeared_near_burner','appeared_near_burner',conditions='door');
machine.add_transition('enter','using_refrigerator','using_refrigerator',conditions='door');
machine.add_transition('moving','entered','entered',conditions='move');
machine.add_transition('moving','appeared_near_burner','appeared_near_burner',conditions='move');
machine.add_transition('moving','using_burner','using_burner',conditions='move');
machine.add_transition('moving','using_refrigerator','using_refrigerator',conditions='move');
machine.add_transition('moving','used_refrigerator','used_refrigerator',conditions='move');
machine.add_transition('moving','nothing','nothing',conditions='moving');
                       
event=['d1_in','u_in','u_in','u_in','r_open','r_close','p_m','u_in','p_m','d1_out'];

print (a.state);
print ('Count:',a.count);
for event in final:
        for i in event:
                a.current=i;
                if(i=='d1_in' or i=='d2_in' or i=='d1_out' or i=='d2_out'):
                        a.entry_exit();
                        print (a.state);
                        print ('count:',a.count);

                elif(i=='r_open' or i=='r_close'):
                        a.using_r();
                        print (a.state);
                
                elif(i=='u_in'):
                        a.using_g();
                        print (a.state);
                '''elif(i=='p_m'):
                        a.moving();
                        print (a.state);'''

sys.exit();
