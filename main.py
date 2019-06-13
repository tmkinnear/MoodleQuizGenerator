# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 14:20:58 2019

@author: tmk5
"""

import generator as gen

myq = gen.process_question_file('example_question_template.quest')

with open(myq.qlabel+'.xml','w') as f:
	f.write(myq.generate_xml())

