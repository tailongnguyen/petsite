# -*- coding: UTF-8 -*-
from models import *
import pandas as pd 

data = pd.read_csv('/home/tailongnguyen/petsite/new.csv')

for i in xrange(2):
    Pet.objects.create(petType='Chó', petName=data['Tên Tiếng Việt'][i], petCode=data['Code'][i], \
        petHistory= data['Nguồn gốc'][i], petAppearance=data['Đặc điểm'][i],  petHabit=data['Tập Tính'][i],\
        lifeSpan_min=int(data['Tuổi thọ (năm)'][i].split('-')[0]), lifeSpan_max=int(data['Tuổi thọ (năm)'][i].split('-')[1]),\
        others=data['Điều kiện sống và chăm sóc'][i])
