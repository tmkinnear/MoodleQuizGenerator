# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 14:20:58 2019

@author: tmk5
"""

import numpy as np

#template for the header of the .xml; takes one string as formatting argument which will be the quiz category name
header = """
<?xml version="1.0" encoding="UTF-8"?>
<quiz>
<!-- question: 0  -->
  <question type="category">
    <category>
        <text>$course$/{0:s}</text>
    </category>
  </question>
"""

#template for the footer of the quiz
footer = """
</quiz>
"""

#template for the numerical questions. Takes five arguments first is question name (not displayed to students), second is question text (supporting html tags) third is value for `correct' answer (should generally be defaulted  to zero, not used in python marking system), the fourth argument is the margin of error (again, default to zero, not used in the python marking system); fifth argument is the question index number
question_numerical = """
<!-- question: {4:03d}  -->
  <question type="numerical">
    <name>
      <text>{0:s}</text>
    </name>
    <questiontext format="html">
      <text><![CDATA[<p>{1:s}<br></p>]]></text>
    </questiontext>
    <generalfeedback format="html">
      <text></text>
    </generalfeedback>
    <defaultgrade>1.0000000</defaultgrade>
    <penalty>0.0000000</penalty>
    <hidden>0</hidden>
    <answer fraction="100" format="moodle_auto_format">
      <text>{2:f}</text>
      <feedback format="html">
        <text></text>
      </feedback>
      <tolerance>{3:f}</tolerance>
    </answer>
    <unitgradingtype>0</unitgradingtype>
    <unitpenalty>0.1000000</unitpenalty>
    <showunits>3</showunits>
    <unitsleft>0</unitsleft>
  </question>
"""


#function for creating the entries for the dropdown lists in fill-in-the-blanks questions. Two arguments, INT number of positions with dropdowns, and a LIST of the options for the dropdowns.
#This version of the function supports only one set of options for all dropdowns.
def question_select_option(nums,opt_sets):
	outtext = ""
	text = """
    <selectoption>
      <text>{0:s}</text>
      <group>{1:d}</group>
    </selectoption>
	"""
	for num in range(nums):
		opts = opt_sets[num].split(',')
		for opt in [opts[0]]:
			outtext+=text.format(opt,num+1)
	for num in range(nums):
		opts = opt_sets[num].split(',')
		for opt in opts[1:]:
			outtext+=text.format(opt,num+1)
	return outtext
	
#generates the fill-in-the-blanks question text. Four arguments. Question name, question text, the LIST of choices and the index number of the question.
def question_select(qtext,question,choice_sets,ind):
	numchoices = 0
	for i in range(100):
		if "[[{0:d}]]".format(i+1) in question:
			numchoices += 1
		else:
			break
	
	#text, question with [[]] choices, options produced from question_select_option
	text = """
	<!-- question: {3:03d}  -->
	  <question type="gapselect">
	    <name>
	      <text>{0:s}</text>
	    </name>
	    <questiontext format="html">
	      <text><![CDATA[<p> {1:s} </p>]]></text>
	    </questiontext>
	    <generalfeedback format="html">
	      <text></text>
	    </generalfeedback>
	    <defaultgrade>1.0000000</defaultgrade>
	    <penalty>0.3333333</penalty>
	    <hidden>0</hidden>
	    <shuffleanswers>0</shuffleanswers>
	    <correctfeedback format="html">
	      <text>Your answer is correct.</text>
	    </correctfeedback>
	    <partiallycorrectfeedback format="html">
	      <text>Your answer is partially correct.</text>
	    </partiallycorrectfeedback>
	    <incorrectfeedback format="html">
	      <text>Your answer is incorrect.</text>
	    </incorrectfeedback>
	    <shownumcorrect/>
		{2:s}
	  </question>
	"""
	options = question_select_option(numchoices,choice_sets)
	return text.format(qtext,question,options,ind)

def format_value(value):
	if type(value) == float:
		return '{0:f}'.format(value)
	elif type(value) == int:
		return '{0:d}'.format(value)
	else:
		return '{}'.format(value)

def answers_multichoice(choices):
	answer_text="""
	<answer fraction="{0:d}"> 
		<text>{1:s}</text> 
	</answer>
	"""
	full_answers = ""
	for i,choice in enumerate(choices):
		value = 100 if i == 0 else 0
		full_answers += answer_text.format(value,format_value(choice))
	return full_answers

def question_multichoice(qtext,question,choices):
	text = """
	<question type="multichoice"> 
	 <name> 
	 	 <text>{0:s}</text> 
	 </name> 
	 <questiontext format="html"> 
	 	<text> <![CDATA[{1:s}]]></text> 
	 </questiontext> 
	{2:s}
	<shuffleanswers>1</shuffleanswers>
	<single>true</single>
</question> """
	answers = answers_multichoice(choices)
	outtext = text.format(qtext,question,answers)
	return outtext

def round_sigfigs(value, sigfig=2):
	if sigfig != None:
		return np.round(value, sigfig - int(np.floor(np.log10(value)))-1)
	else:
		return value

class variable():
	def int_gen(self):
		return np.random.randint(self.low,self.high)
	def float_gen(self):
		if self.sf == None:
			return self.low + np.random.rand()*(self.high-self.low)
		else:
			return round_sigfigs(self.low + np.random.rand()*(self.high-self.low),sigfig=self.sf)
	def const_gen(self):
		return self.value
	def __init__(self,name=None,value=None,function=None,low=None,high=None,opts=None,sf=None):
		self.name = name
		self.value = value
		self.function = function
		self.low = low
		self.high = high
		self.opts = opts
		self.sf = sf
	def regen(self):
		self.value = self.function(self)

def update_values(c,v):
	for vi in v:
		v[vi].regen()
	for ci in c:
		v.update({ci:variable(name=ci, value=parse_calculation(c[ci],v), function=variable.const_gen)})
	return c,v

def parse_questiontext(text,v):
	qtext = text
	for vi in v:
		qtext = qtext.replace('<<{}>>'.format(vi),'{}'.format(v[vi].value))
	return qtext


def parse_calculation(calc,v):
	calc = calc.replace('<<',"v['").replace('>>',"'].value")
	value = eval(calc)
	return value

class question():
	def make_numerical_question(self):
		global question_numerical
		self.c,self.v = update_values(self.c,self.v)
		qtext = parse_questiontext(self.qtext,self.v)
		answer = round_sigfigs(self.v[self.answer].value,self.qoptions['answer_sf'])
		return question_numerical.format(self.qlabel,qtext,answer,self.qoptions['tolerance'],0)
	def make_multichoice_question(self):
		self.c,self.v = update_values(self.c,self.v)
		qtext = parse_questiontext(self.qtext,self.v)
		choices = [round_sigfigs(self.v[self.answer].value,self.qoptions['answer_sf'])]
		for extra_value in range(self.qoptions['choices']-1):
			self.c,self.v = update_values(self.c,self.v)
			choices.append(round_sigfigs(self.v[self.answer].value,self.qoptions['answer_sf']))
		fulltext = question_multichoice(self.qlabel,qtext,choices)
		return fulltext
	def __init__(self,qlabel='Question',v={},c={},qtext=None,answer=None,qtype='multichoice',qoptions={'choices':6,'answer_sf':None,'tolerance':0.01},quantity=1):
		self.v = v
		self.c = c
		self.qlabel = qlabel
		self.qtype = qtype
		self.qtext = qtext
		self.answer = answer
		self.qoptions = qoptions
	def generate_single(self):
		if self.qtype == 'multichoice':
			return self.make_multichoice_question()
		elif self.qtype == 'numerical':
			return self.make_numerical_question()
		else:
			print('!!!!!!')
			return None
	def generate_full(self):
		text = ''
		for i in range(self.quantity):
			text += self.generate_single()
		return text
	def generate_xml(self):
		global header, footer
		myxml = header.format(self.qlabel)
		myxml += self.generate_full()
		myxml += footer
		return myxml
	

def process_question_file(filename):
	valid_qtypes = ['multichoice','numerical']
	question_name = filename.split('.')[0] #split filename apart to get title of quiz
	
	print('Running question generation')
	
	print('Question input file is "{}", question name is "{}"'.format(filename,question_name))
	
	print('Opening and reading {}'.format(filename))
	#open .quiz file and read in all lines of content
	with open(filename,'r') as f:
		template = f.readlines()
	
	template = [ line.replace('\n','').replace('\r','') for line in template ]
	
	print('\tDone!')
	myq = question(qlabel=question_name)
	
	#iterate through all lines in the template file
	for lni,line in enumerate(template):
		ln = lni + 1
		bits = line.split('#')[0].split('\t')
		if len(bits) > 1:
			etype = bits[0] #entry type
			if etype == 'variable':#input
				print('\tAdding variable from line {}'.format(ln))
				var_type = bits[1]
				if var_type == 'constant':
					name = bits[2]
					print('\t\tVariable is a constant of name {}'.format(name))
					if name in myq.v:
						print('\t\t!!Duplicate variable name ({}) found on line {}!!'.format(name,ln))
					value = float(bits[3])
					print('\t\tValue will be {}'.format(value))
					myq.v.update({name:variable(name=name,function=variable.const_gen,value=value)})
				if var_type == 'float':
					name = bits[2]
					print('\t\tVariable is a floating point value of name {}'.format(name))
					if name in myq.v:
						print('\t\t!!Duplicate variable name ({}) found on line {}!!'.format(name,ln))
					low = float(bits[3])
					high = float(bits[4])
					sf = None
					if len(bits) > 5:
						sf = int(bits[5])
					print('\t\tValue will be between {} and {}'.format(low,high))
					myq.v.update({name:variable(name=name,function=variable.float_gen,low=low,high=high,sf=sf)})
				if var_type == 'integer':
					name = bits[2]
					print('\t\tVariable is a integer point value of name {}'.format(name))
					if name in myq.v:
						print('\t\t!!Duplicate variable name ({}) found on line {}!!'.format(name,ln))
					low = float(bits[3])
					high = float(bits[4])
					print('\t\tValue will be between {} and {}'.format(low,high))
					myq.v.update({name:variable(name=name,function=variable.int_gen,low=low,high=high)})
			elif etype == 'calculation':
				print('\tAdding calculation from line {}'.format(ln))
				name = bits[1]
				calculation = bits[2]
				myq.c.update({name:calculation})
				print('\t\tCalculation will be generated from "{}"'.format(calculation))
			elif etype == 'text':
				print('\tAdding question text from line {}'.format(ln))
				myq.qtext = bits[1]
				print('\t\tQuestion text will be generated from "{}"'.format(myq.qtext))
			elif etype == 'type':
				print('\tSetting question type on line {}'.format(ln))
				if bits[1] in valid_qtypes:
					myq.qtype = bits[1]
					print('\t\tQuestion type set as {}'.format(myq.qtype))
				else:
					print('\t\tQuestion type "{}" not valid, skipping'.format(bits[1]))
			elif etype == 'quantity':
				print('\tSetting question variation quantity on line {}'.format(ln))
				myq.quantity = int(bits[1])
				print('\t\tQuantity set as {}, will generate this many variations'.format(myq.quantity))
			elif etype == 'multichoice':
				print('\tSetting multiple choice option on line {}'.format(ln))
				if myq.qtype != 'multichoice':
					print('\t\t!!Note: multichoice option is being set but question type not yet set to multiple choice!!')
				if bits[1] == 'choices':
					myq.qoptions.update({'choices':int(bits[2])})
					print('\t\tSetting number of available choices as {}'.format(myq.qoptions['choices']))
				else:
					print('\t\t!!Suboption {} for multichoice not recognised!!'.format(bits[1]))
			elif etype == 'numerical':
				print('\tSetting numerical question option on line {}'.format(ln))
				if myq.qtype != 'numerical':
					print('\t\t!!Note: numerical question option is being set but question type not yet set to numerical!!')
				if bits[1] == 'tolerance':
					myq.qoptions.update({'tolerance':float(bits[2])})
					print('\t\tSetting answer tolerance as {}'.format(myq.qoptions['tolerance']))
			elif etype == 'answer':
				print('\tSetting answer variable/calculation')
				myq.answer = bits[1]
				if len(bits) > 2:
					myq.qoptions.update({'answer_sf':int(bits[2])})
				print('\t\tAnswer set as {}'.format(myq.qoptions['answer_sf']))
	

	return myq
	
	


