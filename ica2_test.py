import re
import os
import subprocess
import string
from os.path import expanduser
import pandas as pd
import time

home_dir = "."
userchoice = input('\nPlease input the taxonomic group\n').strip().lower()
print('\n')
nums = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
letters = list(string.ascii_lowercase)
checkletters = any(ele in userchoice for ele in letters)
checknums = any(ele in userchoice for ele in nums)
if checkletters == True and checknums == False:
    print('\n')
    print('esearch results are displayed below:\n')
    subprocess.call("esearch -db taxonomy -query %s | efetch -format Gb" % (userchoice), shell=True)
    print('\n')
    output = subprocess.check_output("esearch -db taxonomy -query %s | efetch -format xml | xtract -pattern Taxon -element ScientificName -element TaxId" % (userchoice), shell=True)
    outputdecode = output.decode("utf-8").strip()
    taxonidlist = re.split(r"[\t\n]", outputdecode)
elif checkletters == False and checknums == True:
    print('\n')
    print('esearch results are displayed below:\n')
    subprocess.call("esearch -db taxonomy -query %s[UID] | efetch -format Gb" % (userchoice), shell=True)
    print('\n')
    output = subprocess.check_output("esearch -db taxonomy -query %s[UID] | efetch -format xml | xtract -pattern Taxon -element ScientificName -element TaxId" % (userchoice), shell=True)
    outputdecode = output.decode("utf-8").strip()
    taxonidlist = re.split(r"[\t\n]", outputdecode)
else:
    print('\nInput requires only taxonID or taxonomy, Either "8782" or "aves")')
if len(taxonidlist) == 1:
    print('\nThe esearch for %s taxonomy found no results, please try againp' % (userchoice))
