#Resume Phrase Matcher code


#importing all required libraries
from zipfile import ZipFile
import PyPDF2 as pypdf
import os
from os import listdir
from os.path import isfile, join
from io import StringIO
import pandas as pd
from collections import Counter
import en_core_web_sm
nlp = en_core_web_sm.load()
from spacy.matcher import PhraseMatcher
import matplotlib.pyplot as plt
import shutil
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 


keywordDict=[]

# #Function to read resumes from the folder one by one
# mypath='D:/Resume/Resume/Extracted_pdf' #enter your path here where you saved the resumes
# onlyfiles = [os.path.join(mypath, f) for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
# # file=onlyfiles[1]
# print(onlyfiles)

#function to extract pdfs from uploaded zip file
def extractPdf(filePath):
	with ZipFile(filePath,'r') as zipobject:
		listoffile=zipobject.namelist()
		for filename in listoffile:
	 		if filename.endswith('.pdf'):
	 			zipobject.extract(filename,'Extracted_pdf')


#function to read content of pdfs 
def textExtract(file):
  f=open(file,'rb')
  fileReader=pypdf.PdfFileReader(f)
  pageCount=fileReader.getNumPages()
  count=0
  text=[]
  while count<pageCount:
    pageObj=fileReader.getPage(count)
    count+=1
    t=pageObj.extractText()
    # print(t)
    text.append(t)
    
  f.close()  
  return text

#Function for tokens processing

def createProfile(file):
  text=textExtract(file)
  text=str(text)
  text=text.replace("\\n"," ")
  text=text.replace(","," ")
  text=text.replace("."," ")
  text=text.replace("\""," ")
  text=text.replace("-"," ")
  #Change whole datasheet to lower case
  text=text.lower()
  # print(text)
  global keywordDict
  keywordLabel=keywordDict.columns
  


  # print(keywordLabel)
  countLabel=len(keywordLabel)
  words=['{}_words'.format(a) for a in keywordLabel]
  words=[x.replace(' ','') for x in words]
  mapDict={}
  for w,keywords in zip(words,keywordLabel):
    mapDict[w]=[nlp(text) for text in keywordDict[keywords].dropna(axis=0)]
  # print(mapDict)
  matcher=PhraseMatcher(nlp.vocab)
  for x,y,z in zip(keywordLabel,mapDict,words):
    temp = mapDict[z]
    # print(temp)
    matcher.add(x,None,*temp)
  doc=nlp(text)
  # doc

  d=[]
  matches=matcher(doc)
  for match_id, start, end in matches:
    rule_id = nlp.vocab.strings[match_id]
    span=doc[start:end]
    d.append((rule_id, span.text))
    # print(rule_id)
  keywords = "\n".join(f'{i[0]} {i[1]} ({j})' for i,j in Counter(d).items()) 
  # print(keywords)
  df = pd.read_csv(StringIO(keywords),names = ['Keywords_List'])
  df1 = pd.DataFrame(df.Keywords_List.str.split(' ',1).tolist(),columns = ['Subject','Keyword'])
  df2 = pd.DataFrame(df1.Keyword.str.split('(',1).tolist(),columns = ['Keyword', 'Count'])
  df3 = pd.concat([df1['Subject'],df2['Keyword'], df2['Count']], axis =1) 
  df3['Count'] = df3['Count'].apply(lambda x: x.rstrip(")"))
  # print(df3)

  #############################################
  base=os.path.basename(file)
  filename=os.path.splitext(base)[0]
  name=filename.split('_')[0].upper()
  name1=pd.read_csv(StringIO(name),names=['Candidate Name'])
  dataf = pd.concat([name1['Candidate Name'], df3['Subject'], df3['Keyword'], df3['Count']], axis = 1)
  dataf['Candidate Name'].fillna(dataf['Candidate Name'].iloc[0], inplace = True)
  # print(dataf)
  return(dataf)
  #function ends

#final dataFrame
def finalFrame(onlyfiles):
	# Toaddr=toaddr
	final_database=pd.DataFrame()
	i = 0 
	while i < len(onlyfiles):
	    file = onlyfiles[i]
	    dat = createProfile(file)
	    final_database = final_database.append(dat)
	    i +=1
	    # print(final_database)

	final_database2 = final_database['Keyword'].groupby([final_database['Candidate Name'], final_database['Subject']]).count().unstack()
	final_database2.reset_index(inplace = True)
	final_database2.fillna(0,inplace=True)
	new_data = final_database2.iloc[:,1:]
	new_data.index = final_database2['Candidate Name']
	#execute the below line if you want to see the candidate profile in a csv format
	# sample2=new_data.to_csv('sample.csv')

	plt.rcParams.update({'font.size': 10})
	ax = new_data.plot.barh(title="Resume keywords by category", legend=False, figsize=(25,7), stacked=True)
	labels = []
	for j in new_data.columns:
	    for i in new_data.index:
	        label = str(j)+": " + str(new_data.loc[i][j])
	        labels.append(label)
	patches = ax.patches
	for label, rect in zip(labels, patches):
	    width = rect.get_width()
	    if width > 0:
	        x = rect.get_x()
	        y = rect.get_y()
	        height = rect.get_height()
	        ax.text(x + width/2., y + height/2., label, ha='center', va='center')
	plt.savefig('email.pdf')

def send_mail(toaddr):

	fromaddr="mohitsojitra249@gmail.com"
	Toaddr=toaddr
	#instance of MimeMultipart
	msg= MIMEMultipart()
	# storing the senders email address   
	msg['From'] = fromaddr 
	  
	# storing the receivers email address  
	msg['To'] = Toaddr 
	  
	# storing the subject  
	msg['Subject'] = "YOUR RESULTS FROM DOCSIMPLR ARE HERE!"
	  
	# string to store the body of the mail 
	body = "THANK YOU FOR USING DocSimplr : Making lives of Employers\' easy! \n Your results are attached with this E-Mail."
	  
	# attach the body with the msg instance 
	msg.attach(MIMEText(body, 'plain')) 
	  
	# open the file to be sent  
	filename = "email.pdf"
	attachment = open("email.pdf", "rb") 
	  
	# instance of MIMEBase and named as p 
	p = MIMEBase('application', 'octet-stream') 
	  
	# To change the payload into encoded form 
	p.set_payload((attachment).read()) 
	  
	# encode into base64 
	encoders.encode_base64(p) 
	   
	p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
	  
	# attach the instance 'p' to instance 'msg' 
	msg.attach(p) 
	  
	# creates SMTP session 
	s = smtplib.SMTP('smtp.gmail.com', 587) 
	  
	# start TLS for security 
	s.starttls() 
	  
	# Authentication 
	s.login(fromaddr, "mohit12403") 
	  
	# Converts the Multipart msg into a string 
	text = msg.as_string() 
	  
	# sending the mail 
	s.sendmail(fromaddr, Toaddr, text) 
	  
	# terminating the session 
	s.quit() 

def emptyDir(mypath):
    # os.unlink(email.pdf)
    for filename in os.listdir(mypath):
        file_path = os.path.join(mypath, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def process(filePath,toaddr):
	#Extract pdfs
	extractPdf(filePath)
	#Function to read resumes from the folder one by one
	mypath='./Extracted_pdf' #enter your path here where you saved the resumes
	uploadedR='./UploadedResume'
	onlyfiles = [os.path.join(mypath, f) for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
	global keywordDict
	keywordDict=pd.read_csv("./Classification_Sheet/Classification_Template.csv",encoding='latin-1')
	# file=onlyfiles[1]
	# print(onlyfiles)
	finalFrame(onlyfiles)
	send_mail(toaddr)
	emptyDir(mypath)
	emptyDir(uploadedR)
	# shutil.rmtree(mypath)
	os.remove('email.pdf')
