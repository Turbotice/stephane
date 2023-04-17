# -*- coding: utf-8 -*-

import stephane.web_cv as web_cv

import stephane.web_cv.people as p
import stephane.web_cv.intern as i
import stephane.web_cv.collab as collab
import stephane.web_cv.bibstyle as bibstyle
import stephane.web_cv.genhtml as genhtml

import unicodecsv as ucsv
import csv as csv
import bibtexparser as bib
from yattag import indent

import os

#folder = '/Users/stephane/Documents/Etudiants/Recherche/'
#folder_articles = '/Users/stephane/Documents/Articles/Published/Liste_biblio/'

def filelocations():
    global folder,folder_articles,savefolder
    folderbase = '/Users/stephane/Documents/Site_CV/'

    folder = folderbase+'database/'
    folder_articles = folder
    
    savefolder = folderbase +'Website/Autogen/'

    if not os.path.exists(savefolder):
        os.makedirs(savefolder)
    
def peoplelist(filename='internships.csv'):
    """ Display the list peoples in the console from file internships.csv and collaborators.scv"""
    d = {}
    d['name'] = 'Matthieu Labousse'
    d['aff'] = 'ESPCI'
    d['email'] = ''
    
    ex = p.People(d)
    ex.display()
    
    d = {}
    d['name'] = 'Vincent Bacot'
    d['aff'] = 'University Paris-Diderot'
    d['email'] = ''
    d['dates'] = ''
    
    ex = i.Intern(d)
    ex.display()
    
    print('Students')
    filename = folder+filename
    with open(filename) as csvfile:
        reader = list(csv.DictReader(csvfile,delimiter=';'))
        reader.sort(key=lambda x: x['Year'],reverse=True)
        for row in reader:
            student = i.Intern(row);            
            print(student.display_fancy())
    
    print('')
    print('Collaborators')
    filename = folder+'collaborators.csv' 
    with open(filename) as csvfile:
        reader = list(csv.DictReader(csvfile,delimiter=';'))
        reader.sort(key=lambda x: x['Name'])
        for row in reader:
            student = collab.Collab(row);            
            print(student.display_fancy())
            
def biblio(file='mesarticles.bib'):
    """ Display the list of articles in the console from file"""
    filename = folder_articles+file
           
    with open(filename) as bibtex_file:
        bib_database = bib.load(bibtex_file)
        
        entries = list(bib_database.entries)
        entries.sort(key=lambda x: x['year'],reverse=True)

        for entry in entries:
            print(bibstyle.display(entry,typ='console'))

        print('\n \n \n')
        
        # list option
        print('<ol reversed>')
        for entry in entries:
            print(bibstyle.display(entry,typ='html'))
        print('</ol>')

def biblio_html(file='mesarticles.bib',filename='siteweb/publications.html'):
    """ Generate an html file in filename containing the list of articles from file"""
    filename = folder_articles+file
    print(filename)
    with open(filename) as bibtex_file:
        bib_database = bib.load(bibtex_file)
        print(bib_database.entries)
        entries = list(bib_database.entries)
        entries.sort(key=lambda x: x['year'],reverse=True)

        stringlist = []
        for entry in entries:
            stringlist.append(bibstyle.display(entry,typ='html'))

        doc, tag, text = genhtml.makelist(stringlist,'Publications',order='o',opt=' reversed')

        filename=savefolder+'/publications.html'
        f=open(filename,'w')
        f.write(indent(doc.getvalue()))#.encode('utf-8'))
        f.close()

def peoplelisthtml():
    
    print('Students')
    filename = folder+'internships.csv' 
    with open(filename) as csvfile:
        reader = list(csv.DictReader(csvfile,delimiter=';'))
        reader.sort(key=lambda x: x['Year'],reverse=True)
        
        stringlist = []
        for row in reader:
            print(row['Name'])
            student = i.Intern(row);            
            stringlist.append(student.display_fancy()) 
          
        doc, tag, text = genhtml.makelist(stringlist,'Past supervised students',order='u')

        filename=savefolder+'/students.html'
        f=open(filename,'w')
        f.write(indent(doc.getvalue()))#.encode('utf-8'))
        f.close()
        
    print('Collaborators')
    filename = folder+'collaborators.csv' 
    with open(filename) as csvfile:
        reader = list(csv.DictReader(csvfile,delimiter=';'))
        reader.sort(key=lambda x: x['Name'])
        
        stringlist = []
        for row in reader:
#            print(row['Name'])
            people = collab.Collab(row);            
            stringlist.append(people.display_fancy()) 
          
        doc, tag, text = genhtml.makelist(stringlist,'Collaborators',order='u')

        filename=savefolder+'/collaborators.html'
        f=open(filename,'w')
        f.write(indent(doc.getvalue()))#.encode('utf-8'))
        f.close()

def main():
    """ Generate the people list in html, and the list of articles """
    filelocations()
    peoplelisthtml()
    biblio_html()
    peoplelist()
 
if __name__ == '__main__':
  main()
