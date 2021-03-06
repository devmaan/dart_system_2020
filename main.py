# missile - By: Jiarui - 周三 1月 15 2020

import sensor, image, time, math, imu
from pyb import Servo
from mpu9250 import MPU9250
IMU = MPU9250('X')

time_shut_down = 5 #the time to shut down under no condition (in unit of s)
limit_ready_to_launch = 5 #the longest time between ready and launch (in unit of s)
limit_found_to_hit = 5 #the longest time between found and hit (in unit of s)
green_threshold   = ( 85, 90,-75,-55, 5, 35)
s1 = Servo(1) #aileron 1 horizontal left
s2 = Servo(2) #aileron 2 horizontal right
s3 = Servo(3) #aileron 3 vertical tail
time_found = 0.0
time_ready = 0.0
time_launch = 0.0 #use global variables to write down switch points
K = 50 #the value should be measured
X = 160 #total pixels in x
Y = 120 #total pixels in y
KP = 1 #the value should be measured
k_pitch = 1 #the value should be measured
k_yaw = 1 #the value should be measured
k_roll = 1 #the value should be measured
'''
in the whole program, define x-row, y-pitch, z-yaw.
all positive direction are same.
in case correction needed.
'''
'''
def calculate_kp(flydata):
    kp = 1
    return kp


def imu_stablize(s1_angle, s2_angle, s3_angle, flydata):
    angular_velocity = flydata[0] #[pitch, roll, yaw]

    #pitch Correction
    s1_angle += k_pitch * angular_velocity[0]
    s2_angle -= k_pitch * angular_velocity[0]

    #roll Correction
    s1_angle += k_roll * angular_velocity[1]
    s2_angle += k_roll * angular_velocity[1]

    #yaw Correction
    s3_angle += k_yaw * angular_velocity[2]
    return s1_angle, s2_angle, s3_angle


def servo_change_camera_correction(differ, flydata):
    x_angle, y_angle = differ

    #convert the angle between flight route and the target to the rotate
    #angle of the servos.
    KP = calculate_kp(flydata)
    s1_angle = KP * y_angle
    s2_angle = -KP * y_angle
    s3_angle =  KP * x_angle

    #prevent abnormal rotation
    s1_angle, s2_angle, s3_angle = imu_stablize(s1_angle, s2_angle, s3_angle, flydata)

    servo_act(s1_angle, s2_angle, s3_angle)
    return


def servo_change_imu_stabilize(differ, flydata):
    s1_angle, s2_angle, s3_angle = (0.0, 0.0, 0.0)
    s1_angle, s2_angle, s3_angle = imu_stablize(s1_angle, s2_angle, s3_angle, flydata)

    servo_act(s1_angle, s2_angle, s3_angle)
    return


def imu_correction():
    flydata = readin_imu()
    servo_change_imu_stabilize(differ, flydata)
    return


def camera_correction():
    target_position = readin_sensor()
    flydata = readin_imu()
    differ = target_position[1]
    servo_change_camera_correction(differ, flydata)
    return


def main():
    initialize_imu()
    initialize_servo()

#待机状态 以每秒30帧检测加速度 判断是否起飞
    flydata = readin_imu()
    while (flydata[1] < 0.5): # acceleration < 0.5g
        clock.tick(30)
        flydata = readin_imu()

#起飞后 未找到目标 以大约每秒10帧画面搜索目标
    initialize_sensor()
    t = time.clock()

    f = target_found()
    while (f == False):
        clock.tick(10)
        f = target_found()

#第一次找到目标后 以每秒30帧更新目标状态并调整舵机
    while (time.clock() < time_shut_down):
        clock.tick(30)
        if (target_found()):
            camera_correction()
        else:
            imu_correction()

    IMU.sleep()
    initialize_servo()
    return
'''
'''初始化舵机'''
def initialize_servo():
    s1.angle(0)
    s2.angle(0)
    s3.angle(0)
    return

'''初始化imu'''
def initialize_imu():
    IMU.wake()
    return

'''打开摄像头并初始化'''
def initialize_sensor():
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(time = 100)
    sensor.set_auto_gain(False)
    sensor.set_auto_whitebal(False)
    return

'''读入imu数据，输出陀螺仪数据，roll，pitch，yaw方向加速度，总加速度'''
def readin_imu():
    acceleration, gyro, mag = IMU.sensors()


    acceleration_overall = 0.0
    acceleration_overall += acceleration.x ** 2
    acceleration_overall += acceleration.y ** 2
    acceleration_overall += acceleration.z ** 2
    acceleration_overall = acceleration_overall ** 0.5

    return gyro, acceleration.x, acceleration.y, acceleration.z, acceleration_overall

'''输入摄像头读入的图像，输出目标距离摄像头的距离，目标方向和roll指向的夹角（偏右，偏上）'''
def readin_sensor(img):
    blobs = img.find_blobs([green_threshold])
    area_total, x_pix, y_pix = (0.0, 0.0, 0.0)

    if blobs:
        for b in blobs:
            ROI = (b[0],b[1],b[2],b[3])
            img.draw_rectangle(b[0:4]) # rect
            img.draw_cross(b[5], b[6]) # cx, cy
            area = b[2] * b[3]
            x_pix += b[5]*area
            y_pix += b[6]*area
            area_total += area

    x_pix /= area_total
    y_pix /= area_total
    x_angle = math.atan(K * x_pix)
    y_angle = math.atan(K * y_pix)
    angle = (x_angle, y_angle)

    if len(blobs) == 1:
        b = blobs[0]
        Lm = (b[2]+b[3])/2
        distance = K/Lm

    return distance, angle

'''检查是否到达发射前准备状态，是否转正'''
def check_ready():

    return ifready

'''检查roll方向加速度是否大于0.5g '''
def check_launch():
    flydata = readin_imu()
    iflaunch = (flydata[1] > 0.5)
    return iflaunch

'''输入imu读入的数据，检查imu读入的数据是否在正常范围之内'''
def check_imu_data(flydata):

    return if_imu_correct

'''输入图像，检查是否识别到目标'''
def check_target_found(img):
    blobs = img.find_blobs([green_threshold])
    if (len(blobs) >= 1):
        green_block_found = True
    else:
        green_block_found = False
    return green_block_found

'''检查图像中绿色色块的大小是否超过阈值'''
def check_hit():

    return ifhit

'''根据飞行数据计算servo转动参数'''
def calculate_kp():
    flydata = readin_imu()

    return KP

'''根据flydata计算稳定阶段servo应该转动以维持飞行平稳的角度'''
def calculate_imu_change(flydata):

    return s1_angle, s2_angle, s3_angle

'''计算aim阶段servo应该转动以朝向目标的角度'''
def calculate_camera_change(img):
    target_position = readin_sensor(img)
    differ = target_position[1]
    x_angle, y_angle = differ

    #convert the angle between flight route and the target to the rotate
    #angle of the servos.
    KP = calculate_kp()
    s1_angle = KP * y_angle
    s2_angle = -KP * y_angle
    s3_angle =  KP * x_angle
    return s1_angle, s2_angle, s3_angle

'''aim阶段为维持飞行相对平稳修正servo转动角度'''
def calculate_imu_adapt(s1_angle, s2_angle, s3_angle):
    flydata = readin_imu()
    if (check_imu_data(flydata)):

    return s1_angle, s2_angle, s3_angle

'''servo转动'''
def act_servo(s1_angle, s2_angle, s3_angle):
    s1.angle(s1_angle)
    s2.angle(s2_angle)
    s3.angle(s3_angle)
    return

'''关闭imu，舵机恢复原位'''
def control_shutdown():
    IMU.sleep()
    initialize_servo()
    #command needed: turn off camera
    '''
    control_rest() #should restart or not?
    '''
    return 0

'''aim阶段 可以跳到stablize及shutdown'''
def control_aim(img0):
    global time_found
    img = img0
    t2 = time.clock()
    while ( t2 - time_found < limit_found_to_hit ):
        clock.tick(40)
        s1_angle, s2_angle, s3_angle = calculate_camera_change(img)
        s1_angle, s2_angle, s3_angle = calculate_imu_adapt(s1_angle, s2_angle, s3_angle)
        act_servo(s1_angle, s2_angle, s3_angle)
        img = sensor.snapshot()
        iffound = check_target_found(img)
        if (! iffound):
            i = 0
            while (i < 3) and (! iffound):
                clock.tick(120)
                i += 1
                img = sensor.snapshot()
                iffound = check_target_found(img)
            if (i == 3):
                control_stablize() #check for 3 times
        t2 = time.clock()
        if (check_hit()):
            break
    control_shutdown()
    return 0

'''stablize阶段 可转到aim'''
def control_stablize():
    global time_launch
    img = sensor.snapshot()
    iffound = check_target_found(img)
    while (! iffound):
        clock.tick(30)
        flydata = readin_imu()
        if (check_imu_data(flydata)):
            s1_angle, s2_angle, s3_angle = calculate_imu_change(flydata)
            act_servo(s1_angle, s2_angle, s3_angle)
        img = sensor.snapshot()
        iffound = check_target_found(img)
    global time_found
    time_found = time.clock()
    control_aim(img)
    return 0

'''检验是否发射阶段 可转到stablize ready'''
def control_launch():
    global time_ready
    iflaunch = check_launch()
    while (! iflaunch):
        clock.tick(50)
        t1 = time.clock()
        if (t1 - time_ready > limit_ready_to_launch):
            control_ready()
        iflaunch = check_launch()
    global time_launch
    time_launch = time.clock()
    control_stablize()
    return 0


def control_ready():
    ifready = check_ready()
    while (! ifready):
        clock.tick(10)
        ifready = check_ready()
    initialize_sensor()
    global time_ready
    time_ready = time.clock()
    control_launch()
    return 0


def control_rest():
    initialize_servo()
    initialize_imu()
    t = time.clock()
    global time_found
    time_found = time.clock()
    global time_launch
    time_launch = time.clock()
    global time_ready
    time_ready = time.clock()
    return t


def main():
    t0 = control_rest()
    control_ready()
    return 0


main()
