import matplotlib.pyplot as plt
import time
import datetime
import math
import statistics

start = time.process_time()

first = True
start_time = 0
def to_time(date):
	global first
	global start_time
	if(first):
		first = False
		start_time = float(datetime.datetime.strptime(date, "%d-%m-%Y %H:%M:%S.%f").strftime('%s.%f'))%10000
		return 0
	else:
		return float(datetime.datetime.strptime(date, "%d-%m-%Y %H:%M:%S.%f").strftime('%s.%f'))%10000 - start_time

start = time.process_time()
filename = 'Vivo 1716/car_on_pocket/accelerometer Dec 09 121014.txt'
with open('BTP_data/'+filename) as f:
	lines = f.readlines()
	lines = lines[648::2]
	time_list = [to_time(line.split(',')[0]) for line in lines]		#time
	x = [float(line.split(',')[1]) for line in lines]		#x-axis
	y = [float(line.split(',')[2]) for line in lines]		#y-axis
	z = [float(line.split(',')[3]) for line in lines]		#z-axis

n = len(x)
print(n)
mod = []
for i in range(n):
	mod.append(math.sqrt(x[i]*x[i] + y[i]*y[i] + z[i]*z[i]))

new_x = []
new_y = []
new_z = []
new_mod = []
new_time = []

theta = 0

phi = 0
phi_l = []
psy = 0

time_of_latest_psy_calculation = 0

def cal_phi_and_theta(ax, ay, az):
	global theta
	global phi
	
	theta = math.acos(az/9.8)
	
	if(ax == 0):
		phi = 1.57079632679
	else:
		phi = math.atan(ay/ax)

def cal_tilt(az):
	global theta
	theta = math.acos(az/9.8)
	#print('theta', theta)

def cal_phi(ax,ay):
	global phi
	if(ax == 0):
		phi = 1.57079632679
	else:
		phi = math.atan(ay/ax)
	#print('phi', phi)

def cal_psy(i):
	global theta
	global phi
	global psy
	
	initial_time = time_list[i]
	tempx = []
	tempy = []
	tempz = []
	for j in range(i, n):
		if time_list[j] - time_list[i] < 1.5:
			tempx.append(x[j])
			tempy.append(y[j])
			tempz.append(z[j])
		else:
			end_time = time_list[j]
			break
	
	ax = sum(tempx)/len(tempx)
	ay = sum(tempy)/len(tempy)
	az = sum(tempz)/len(tempz)
	
	psy = math.atan( (-ax*math.sin(phi) + ay*math.cos(phi)) / ( (ax*math.cos(phi) + ay*math.sin(phi))*math.cos(theta) - az*math.sin(theta) ) )
	
	print('psy',psy)

def ret_ori_data(i):
	global theta
	global phi
	global psy
	
	sin_theta = math.sin(theta)
	cos_theta = math.cos(theta)
	
	sin_phi = math.sin(phi)
	cos_phi = math.cos(phi)
	
	sin_psy = math.sin(psy)
	cos_psy = math.cos(psy)
	
	ax = x[i]
	ay = y[i]
	az = z[i]
	
	tx = cos_psy*(cos_phi*(ax*cos_theta - ay*sin_theta) + az*sin_phi) - sin_psy*(ax*sin_theta + ay*cos_theta)
	
	ty = sin_psy*(cos_phi*(ax*cos_theta - ay*sin_theta) + az*sin_phi) + cos_psy*(ax*sin_theta + ay*cos_theta)
	
	tz = sin_phi*(ay*sin_theta - ax*cos_theta) + (az*cos_phi)
	
	return tx,ty,-tz

start_reorient = False
ax_for_median = []
ay_for_median = []
az_for_median = []
for i in range(n):
	if(time_list[i] > 0 and time_list[i] < 20):
		ax_for_median.append(x[i])
		ay_for_median.append(y[i])
		az_for_median.append(z[i])
		#print("Cal 1 and 2")
	elif (time_list[i] >= 20 and (theta == 0 or phi == 0)):
		cal_phi_and_theta(statistics.median(ax_for_median), statistics.median(ay_for_median), statistics.median(az_for_median))
	
	if ( (mod[i] > 10.0) and (time_list[i] - time_of_latest_psy_calculation > 2) and theta!=0 and phi!=0):
		cal_psy(i)
		time_of_latest_psy_calculation = time_list[i]
		start_reorient = True
		print("psy calculated at", time_list[i], " and mod: ", mod[i])
	
	if (start_reorient):
		#print("Reorienting")
		tx,ty,tz = ret_ori_data(i)
		new_x.append(tx)
		new_y.append(ty)
		new_z.append(tz)
		new_mod.append(math.sqrt(tx*tx + ty*ty + tz*tz))
		new_time.append(time_list[i])

print(len(new_x))

plt.plot(new_time, new_x, label = "X-Axis")
plt.plot(new_time, new_y, label = "Y-Axis")
plt.plot(new_time, new_z, label = "Z-Axis")
plt.plot(new_time, new_mod, label = "Mod")
plt.xlabel('Time (in seconds)')
# Set the y axis label of the current axis.
plt.ylabel('Magnitude')
# Set a title of the current axes.
plt.title(filename)
# show a legend on the plot
plt.legend()
print('Time taken: ', time.process_time() - start)
# Display a figure.
#plt.show()
plt.savefig('Plots/Ori2/'+filename.replace('/','_')+'.svg', format = 'svg')
plt.close()


















