import re
import os
import subprocess
import string
from os.path import expanduser
import pandas as pd
import time

#######  OBTAININGE TAXON ID FROM USER  #######
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

taxonidlist, home_dir = gettaxonid()