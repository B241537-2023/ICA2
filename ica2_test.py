import re
import os
import subprocess
import string
from os.path import expanduser
import pandas as pd
import time

#######  1. OBTAININGE TAXON ID FROM USER  #######
def gettaxonid ():
    # saving the users home directory path as a variable
    home_dir = "."
    userchoice = input('\nPlease input the taxonomic group\n').strip().lower()
    print('\n')
    # Creating a list of numbers 0-9 and a list of the letter of the alphabet to check against the users input
    nums = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    letters = list(string.ascii_lowercase)
    checkletters = any(ele in userchoice for ele in letters)
    checknums = any(ele in userchoice for ele in nums)
    # Checks if user input was alphabetical, and then perform esearch
    if checkletters == True and checknums == False:
        print('\n')
        print('esearch results are displayed below:\n')
        # Displays esearch results in genebank format
        subprocess.call("esearch -db taxonomy -query %s | efetch -format Gb" % (userchoice), shell=True)
        print('\n')
        output = subprocess.check_output("esearch -db taxonomy -query %s | efetch -format xml | xtract -pattern Taxon -element ScientificName -element TaxId" % (userchoice), shell=True)
        outputdecode = output.decode("utf-8").strip()
        # a list containing the taxon and taxonIDs from esearch results is created
        taxonidlist = re.split(r"[\t\n]", outputdecode)
    # Checks if user input was numerical, and then performs esearch
    elif checkletters == False and checknums == True:
        print('\n')
        print('esearch results are displayed below:\n')
        # Displays esearch results in genebank format
        subprocess.call("esearch -db taxonomy -query %s[UID] | efetch -format Gb" % (userchoice), shell=True)
        print('\n')
        output = subprocess.check_output("esearch -db taxonomy -query %s[UID] | efetch -format xml | xtract -pattern Taxon -element ScientificName -element TaxId" % (userchoice), shell=True)
        outputdecode = output.decode("utf-8").strip()
        # a list containing the taxon and taxonIDs from esearch results is created
        taxonidlist = re.split(r"[\t\n]", outputdecode)
    else:
        print('\nInput requires only taxonID or taxonomy, Either "8782" or "aves")')
        taxonidlist = gettaxonid()
    # Checking if the esearch had valid output.
    if len(taxonidlist) == 1:
        print('\nThe esearch for %s taxonomy found no results.' % (userchoice))
        taxonidlist = gettaxonid()
    return taxonidlist, home_dir

#######  2. CHECKING FOR MULTIPLE RESULTS  #######
def checktaxid (idlist):
    # If length of list is greater than 3, the Taxon esearch generated more than one output
	if len(idlist) > 3:
    # Asks the user to input one of the available options from the esearch
		choice = input('\nPlease type the name of the desired output\n').strip().lower().capitalize()
		if choice in idlist:
			for item in idlist:
                # If the input matched an element from the list, 
                # items apart from the users choice will be deleted from the list
				if item == choice:
					index = idlist.index(item)
					del idlist[:index]
					del idlist[index + 2:]
        # If theinput was not one of the available options on the list, the function will restart
		else:
			print('\nYou did not input one of the available choices')
			idlist = checktaxid(idlist)
    # taxonIDs get updated, this creates a list, with 3 elements, Taxon name, TaxonID new, TaxonID old.
    # the old taxon ID will be deleted
	elif len(idlist) == 3:
		del idlist[2:]
    # If list length is 2, this Taxon esearch generated a single taxon.
	elif len(idlist) == 2:
		return idlist
	return idlist


taxonidlist, home_dir = gettaxonid()
newidlist = checktaxid(taxonidlist)