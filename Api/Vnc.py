from fastapi import FastAPI, Request, APIRouter
from pydantic import BaseModel
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from Api import Getvm
import datetime
import random
import string
import asyncio
import subprocess
import socket
import os

APP = FastAPI()
router = APIRouter(tags=['vnc'])

scheduler = BackgroundScheduler()
scheduler.start()

# 存储每个会话ID对应的vnctoken和过期时间
session_data = {}

def process_expired_session(session_id, vm_name):
    # 模拟处理会话过期的任务
    #print(f"处理会话 {session_id} 的过期任务开始")
    # 在这里添加你的任务逻辑
    #print(f"处理会话 {session_id} 的过期任务完成")
	delete_account("vnc_" + vm_name)
	print(f"处理会话 {session_id + ' ' + 'vnc_'+vm_name} 的过期任务完成")

class Login(BaseModel):
    toekn: str
    session_id: str
    id_d: str
    expiration_time: Optional[datetime.datetime] = None

class Logout(BaseModel):
    toekn: str
    session_id: str

class State(BaseModel):
    toekn: str
    session_id: str
	
@router.post("/login")
async def login(login: Login):
    session_id = login.session_id
    expiration_time = login.expiration_time or (datetime.datetime.now() + datetime.timedelta(minutes=15))
    # 获取任务列表
    jobs = scheduler.get_jobs()

    # 检查是否已经存在一个与当前会话ID关联的任务
    for job in jobs:
        if session_id in job.args:
            # 返回这个任务的数据，包括vnctoken和过期时间
            return {"code": "1", "message": 'Logged in successfully', "vnctoken": session_data[session_id]['vnctoken'], "expiration_time": session_data[session_id]['expiration_time'].isoformat(), 'id_d': session_data[session_id]['id_d'].isoformat(), 'vm_name': session_data[session_id]['vm_name'].isoformat(), 'nodeip': session_data[session_id]['nodeip'].isoformat(),'state': "enabled"}

    # 如果不存在与当前会话ID关联的任务，那么添加一个新任务

    vnctoken = generate_random_string()
    vm_name = Getvm.get_name(login.id_d)
    create_account('vnc_' + vm_name, login.id_d[0:8] + vnctoken)
    session_data[session_id] = {'vnctoken': vnctoken, 'expiration_time': expiration_time, 'id_d': login.id_d, 'vm_name': 'vnc_' + vm_name, 'nodeip': nodeip()}
    scheduler.add_job(process_expired_session, 'date', run_date=expiration_time, args=[session_id, vm_name])
    return {"code": "0","message": 'Logged in successfully', "expiration_time": expiration_time.isoformat(), "vnctoken": vnctoken, 'id_d': login.id_d, 'vm_name': 'vnc_' + vm_name, 'nodeip': nodeip(), 'state': "enabled"}

@router.post("/logout")
async def logout(logout: Logout):
    #session_id = request.query_params.get('session_id')
    session_id = logout.session_id
    # 获取任务列表
    jobs = scheduler.get_jobs()
    for job in jobs:
        # 如果任务的参数中包含当前会话的ID，那么立即执行并移除这个任务
        if session_id in job.args:
            job.func(*job.args)  # 立即执行任务
            scheduler.remove_job(job.id)  # 移除任务
    return {"code": "0", "message": "操作成功"}

@router.post("/state")
async def state(state: State):
    session_id = state.session_id
    ip = ip()
    # 获取任务列表
    jobs = scheduler.get_jobs()
    for job in jobs:
        # 如果任务的参数中包含当前会话的ID，那么立即执行并移除这个任务
        if session_id in job.args:
            return {"code": "0", "message": 'Logged in successfully', "vnctoken": session_data[session_id]['vnctoken'], "expiration_time": session_data[session_id]['expiration_time'].isoformat(), 'id_d': session_data[session_id]['id_d'].isoformat(), 'state': "enabled", 'nodeip': nodeip()}
    return {"code": "1", "message": "注销", 'state': "disabled"}

def generate_random_string(length=4):
    # 定义所有可能的字符，只包括大小写字母和数字
    all_chars = string.ascii_letters + string.digits
    all_chars = all_chars.replace('z', '').replace('Z', '')

    # 使用random.choices随机选择4个字符
    random_chars = random.choices(all_chars, k=length)

    # 使用join把字符列表转换成字符串
    return ''.join(random_chars)

#获取本机ip
def nodeip():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('8.8.8.8', 80))
	nodeip = s.getsockname()[0]
	return nodeip

def create_account(username, password):
    # 创建Windows账户
    command = f"net user {username} {password} /add"
    subprocess.run(command, shell=True)

    # 将账户加入Hyper-V Administrators组
    command = f"net localgroup \"Hyper-V Administrators\" {username} /add"
    subprocess.run(command, shell=True)
	
def delete_account(username):
    # 删除Windows账户
    command = f"net user {username} /delete"
    subprocess.run(command, shell=True)