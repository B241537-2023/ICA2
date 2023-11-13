import re
import os
import subprocess
import string
import pandas as pd

#  OBTAININGE TAXON ID FROM USER  #


def gettaxonid():
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
        subprocess.call("esearch -db taxonomy -query %s | efetch -format Gb" %
                        (userchoice), shell=True)
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


#  CHECKING FOR MULTIPLE RESULTS  #


def checktaxid(idlist):
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


#  OBTAINING NAME OF PROTEIN  #
def getprotein(idlist):
    # Ask the user to input the protein of interest
    protchoice = input('\nPlease specify your family of Protein of interest for the %s taxon\n' % (idlist[0])).strip().lower()
    return protchoice

#  OBTAINING WORK DIRECTORY NAME  #


def get_available_name(base_name, existing_folders):
    number = 1
    new_name = base_name
    while new_name in existing_folders:
        number += 1
        new_name = f"{base_name}_{number}"
    return new_name


def create_folder(folder_name):
    try:
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created successfully.")
        return folder_name
    except FileExistsError:
        return None


def get_folder_name():
    default_folder = 'data'
    folder_name = input(f"Enter data folder name (default: {default_folder}): ").strip() or default_folder
    return folder_name


def getworkpath():
    while True:
        folder_name = get_folder_name()
        if (created_folder := create_folder(folder_name)) is not None:
            return created_folder
        else:
            user_response = input(f"Folder '{folder_name}' already exists.\n"
                                  "Do you want to\n1. Remove it\n2. Rename it\n3. Choose a different name?\nEnter the number:\n")

            if user_response == '1':
                try:
                    os.rmdir(folder_name)
                    print(f"Folder '{folder_name}' removed.")
                except OSError as e:
                    print(f"Error removing folder: {e}")
            elif user_response == '2':
                new_name = get_available_name(folder_name, os.listdir())
                print(f"Suggested new name: '{new_name}'")
                return create_folder(new_name)
            elif user_response == '3':
                print("Operation canceled. Please choose a different folder name.")
                continue
            else:
                print("Invalid option. Please choose 1, 2, or 3.")
    
#  CREATING SPECIES, TAXID, ACCESSION AND PROTEIN LENGTH LISTS FROM ESEARCH RESULTS #


def listmaker(workpath):
    # Creating the list of species names 
    tempcmd = "cat %s/docsum.txt | xtract -pattern Organism -element Organism" % (workpath)
    protspecies = subprocess.check_output(tempcmd, shell=True)
    protspeciesdec = protspecies.decode("utf-8").strip()
    protspecieslist = re.split(r"[\n]", protspeciesdec)
    # Creating the list of taxonIDS
    protspeciestaxid = subprocess.check_output("cat %s/docsum.txt | xtract -pattern DocumentSummary -element TaxId" % (workpath), shell=True)
    protspeciestaxiddec = protspeciestaxid.decode("utf-8").strip()
    protspeciestaxidlist = protspeciestaxiddec.split()
    # Creating the list of Protein Accession numbers 
    protspeciesaccession = subprocess.check_output("cat %s/docsum.txt | xtract -pattern DocumentSummary -element AccessionVersion" % (workpath), shell=True)
    protspeciesaccessiondec = protspeciesaccession.decode("utf-8").strip()
    protspeciesaccessionlist = protspeciesaccessiondec.split()
    # Creating the list of Protein lengths
    protlength = subprocess.check_output("cat %s/docsum.txt | xtract -pattern DocumentSummary -element Slen" % (workpath), shell=True)
    protlengthdec = protlength.decode("utf-8").strip()
    protlengthlist = protlengthdec.split()
    # Converting protein length list from a string to integers
    protlengthlistint = list(map(int, protlengthlist))
    return protspecieslist, protspeciestaxidlist, protspeciesaccessionlist, protlengthlistint

# CHECKING SEQUENCES WITH TAXID AND PROTEIN  #


def checkseq(idlist, protchoice, home_dir, workpath):
    # Asks the user to input protein search option
    choiceg = ""
    print('\n')
    print('Would you rather:\n\n1. eSearch with:\n\t"TaxonID: %s"\n\t"Protein name: %s"\n\nWARNING: conservation plot would not be as biologically significant\n\n\n2. eSearch with:\n\t"TaxonID: %s"\n\t"Protein name: %s"\n\t"Gene name: to be specified"\n\nWARNING: This would produce a biologically significant conservation plot, but fewer species will be covered' % (idlist[1], protchoice, idlist[1], protchoice))
    print('\n')
    # While True loop here acts as an error trap.
    while True:
        choice = input('Please input 1 or 2\n').strip()
        # performing esearch with taxid, protein and gene name
        if choice == '2':
            choiceg = input('\nPlease enter the gene name\n').strip()
            # performing esearch
            subprocess.call("esearch -db protein -query 'txid%s[Organism:exp] AND %s AND %s[Gene Name] NOT PARTIAL' | efetch -format docsum > %s/docsum.txt" % (idlist[1], protchoice, choiceg, workpath), shell=True)
            # Running previous function will make all lists required to create the panda dataframe from results
            protspecieslist, protspeciestaxidlist, protspeciesaccessionlist, protlengthlistint = listmaker(workpath)
            break
        # performing esearch with taxID and protein
        elif choice =='1':
            # performing esearch
            equery = "esearch -db protein -query 'txid%s[Organism:exp] AND %s NOT PARTIAL' | efetch -format docsum > %s/docsum.txt" % (idlist[1], protchoice, workpath)
            subprocess.call(equery, shell=True)
            # Running previous function will make all lists required to create the panda dataframe from results   
            protspecieslist, protspeciestaxidlist, protspeciesaccessionlist, protlengthlistint = listmaker(workpath)
            break
        else:
            print('INVALID INPUT, please try again')

    # generating panda dataframe using the lists created with function 4.0
    s1 = pd.Series(protspecieslist)
    s2 = pd.Series(protspeciestaxidlist)
    s3 = pd.Series(protspeciesaccessionlist)
    s4 = pd.Series(protlengthlistint)
    # These are the dataframe columns: Species Name, Species TaxID, Protein Accession, Protein length
    df = pd.DataFrame({'Species Name' : s1, 'Species TaxID' : s2, 'Prot Accession' : s3, 'Prot Length' : s4})
    # Obtaining the total number of sequences by using the first index of the df.shape
    totalseq = df.shape[0]
    # Obaining the total number of unique species
    uniquespecies = len(df.drop_duplicates('Species Name'))
    # the following will occur if the total number of sequences found from the esearch is less than 10
    if totalseq < 10:
        print('fewer than 10 sequences were found')
        print('\n')
        print('fewer than 10 sequences were found:\n\nTaxon          :   %s\nProtein Family :   %s\nTotal sequences:   %s\nNo. of Species :   %s' % (idlist[0], protchoice, totalseq, uniquespecies))
        print('\n')
        # Creating a list of species names 
        protspeciesl = df['Species Name'].tolist()
        # Creating a dictionary of Species : Sequence counts
        numberoffasta = dict((x, protspeciesl.count(x)) for x in set(protspeciesl))
        print('The number of FASTA sequences for each of the different species are displayed below:\n')
        # all the unique species and their number of sequences are then displayed to the user
        for key, value in numberoffasta.items():
            print('Species: %-40s' 'Number of FASTA sequences: %s' %(key, numberoffasta[key]))
        print('\n')
        print('The results contain redundant sequences.\nFASTA sequences will be downloaded later, and redundant sequences will be removed.')
        print('\n')
        return protchoice, protspeciesl, choiceg, df
    # the following will occur if the total number of unique sequences found	from the esearch is less than 10
    if uniquespecies < 5:
        print('\n')
        print('Fewer than 5 unique sequences were found:\n\nTaxon          :   %s\nProtein Family :   %s\nTotal sequences:   %s\nNo. of Species :   %s' % (idlist[0], protchoice, totalseq, uniquespecies))
        print('\n')
        # Creating a list of species names
        protspeciesl = df['Species Name'].tolist()
        # Creating a dictionary of Species : Sequence counts
        numberoffasta = dict((x, protspeciesl.count(x)) for x in set(protspeciesl))
        print('The number of FASTA sequences for each of the different species are displayed below:\n')
        # all the unique species and their number of sequences are then displayed	to the user
        for key, value in numberoffasta.items():
            print('Species: %-40s' 'Number of FASTA sequences: %s' %(key, numberoffasta[key]))
        print('\n')
        print('The results contain redundant sequences.\nFASTA sequences will be downloaded later, and redundant sequences will be removed.')
        return protchoice, protspecieslist, choiceg, df
    # Prints esearch output summary: total number of sequences, number of unique species
    print('\n')
    print('Results from the esearch are displayed below:\n\nTaxon          :   %s\nProtein Family :   %s\nTotal sequences:   %s\nNo. of Species :   %s' % (idlist[0], protchoice, totalseq, uniquespecies))
    print('\n')
    # Creating a list of species names
    protspeciesl = df['Species Name'].tolist()
    # Creating a dictionary of Species : Sequence counts)
    numberoffasta = dict((x, protspecieslist.count(x)) for x in set(protspecieslist))
    # Printing the top 3 most represented species. 
    # Achieved bysorting the dictionary from highest to loweres and appending the top 3 to a list
    print('The top 3 most species are displayed below:\n')
    highestkey = sorted(numberoffasta, key=numberoffasta.get, reverse=True)[:3]
    highestvalue = []
    for item in highestkey:
        value = numberoffasta.get(item)
        highestvalue.append(value)
    print('\nSpecies: %-40s Sequences: %s\nSpecies: %-40s Sequences: %s\nSpecies: %-40s Sequences: %s\n' % (highestkey[0], highestvalue[0], highestkey[1], highestvalue[1], highestkey[2], highestvalue[2]))
    print('\n')
    print('The results contain redundant sequences.\nFASTA sequences will be downloaded later, and redundant sequences will be removed.')
    print('\n')
    # view = input('\nWould you like to view the full list of species and their respective number of FASTA sequences? y/n\n')
    # Print the key of the dictionary (species), followed by the count (value) will be printed to the user
    for key, value in numberoffasta.items():
        print('Species: %-40s' 'Number of FASTA sequences: %s' %(key, numberoffasta[key]))
    return protchoice, protspeciesl, choiceg, df


# DETERMINING IF THE OUTPUT IS THE DESIRED OUTPUT  #


def change(idlist, protchoice, choiceg, home_dir, df, workpath):
    return protchoice, idlist, choiceg, df, workpath

# WARNING THE USER OF THE PRESENCE OF SEQUENCES WITH LOW/HIGH STANDARD DEVIATIONS


def checkingstandarddeviation(df):

    # first step is to obtain the shortest length protein from the dataframe, this is saved as a variable called min
    min = df['Prot Length'].min()
    # next the longest protein must be obtained and saved as a variable called max
    max = df['Prot Length'].max()
    # then we must get the mean length of proteins within the data frame and save this as a variable
    mean =df['Prot Length'].mean()
    # using the above three variables, the standard deviation of each of the lengths of proteins within the dataframe can be calculated
    std = df['Prot Length'].std()
    totalabove = 0
    totalbelow = 0
    # the mean, standard deviation and the min and max of each protein sequence is then displayed to the user
    print('\n')
    print('Protein Length Statistics:\n\n\tMinimum Length:                  %s\n\tMaximum Length:                  %s\n\tMean Length:                     %.2f\n\tStandard Deviation:             %.2f' % (min, max, mean, std))
    # if the max sequence length is found to be >1 std above or below the mean, the following will be displayed to the user
    if max > (mean + std) or min < (mean - std):
        print('\nATTENTION')
        print('\nthe max or min length protein is >1 std from the mean')
        print('\nif this is the case, then there is a possibility of the presence of an outlier')
        print('\nYou may want to consider removing certain sequences')
    return min, max, mean, std

# DISPLAYING TO THE USER THE NUMBER OF SEQUENCES WHOSE STDs ARE ABOVE THE MEAN AND ALLOWING THEIR REMOVAL


def standarddeviationabove(df, min, max, mean, std):
    # while loop here acts as an error trap, this is here if the user does not enter one of the required inputs
    while True:
        # if the largest protein length if more than 1 std above the mean, the following will occur:		
        if max > (mean + std):
            print("\nMAXIMUM LENGTH SEQUENCE IS >1 STD ABOVE THE MEAN\n")
            print('\n\t-Choice-\t-Action-')
            print('\t0\t:\t[DO NOT REMOVE]    any sequences')
            stdabovecheck = mean
            n = 1
            # another while loop which looks for sequences with std above the mean protein length
            # with each time this loop goes around the number of stds will increases, unless zero standard deviations are found or if it reaches the value of 5
            while stdabovecheck < max and n <= 5:
                stdabovecheck = mean + std*n
                stdabove = df[df.apply( lambda x : x['Prot Length'] > (mean + std*n), axis=1 )].shape[0]
                if stdabove == 0:
                    break
                print('\t%s\t:\t[REMOVE SEQUENCES] %s Sequences     that are     %s Standard Deviations above the Mean' % (n, stdabove, n))
                totalabove = n
                n += 1
            # the user will be faced with a decision based on information obtained from the above commands
            # the user will be asked to provide the script with a digit
            choice = input('\nplease input a digit of your choosing, the sequences to be removed will be displayed after your choice has been made\n').strip()
            # a list containing options for the user must is created
            a = range(0, totalabove + 1)
            stdabovelist = list(map(str, a))
            # the list is referenced to the user to check if the user input was valid
            check = any(item in choice for item in stdabovelist) 
            if check == True:
                # the input of the user determines the number of sequences that the user wants to remove
                # if the input is 0, the following will occur
                if choice == "0":
                    print('\n')
                    return df
                else:
                    # if the user input is not 0, the actual number of stds above the mean have been inputted by the user
                    # the user input must be converted into an integer
                    choice = int(choice)
                    # the script will then go on to locate the sequence that need to be removed
                    # once these sequence have been identified they are saved into a new dataframe, once this has occured the index is reset
                    stdaboveremove = df[df.apply( lambda x : x['Prot Length'] > (mean + std*choice), axis=1 )]
                    stdaboveremove1 = stdaboveremove.reset_index(drop=True, inplace=True)
                    # these particular sequences are now to be removed from the dataframe and saved to a new one
                    newdf = df[~df.apply( lambda x : x['Prot Length'] > (mean + std*choice), axis=1 )]
                    print('\n')
                    # the dataframe containing the sequences that are to be removed is displayed to the user
                    # the user is asked if they are happy with the removal of these sequences
                    print(stdaboveremove)
                    choices = input('\nyou have chosen for these sequences to be removed from the dataframe, are you happy with this decision? y/n\n').strip().lower()
                    # if the user is happy with their decision and inputs y, the datafram is saved with the selected sequences removed, the function ends
                    if choices == "y":
                        print('\n')
                        return newdf
                    # if the user is not happy with their decision and inputs n, the function will restart
                    elif choices == "n":
                        print('\nlets try that again, please select the sequences to be removed again\n')
                    else:
                        print('\nINVALID INPUT PLEASE TRY AGAIN')
            else:
                    print('\n')
                    print('INVALID INPUT, PLEASE TRY AGAIN')

# DISPLAYING TO THE USER THE NUMBER OF SEQUENCES WHOSE STDs ARE BELOW THE MEAN AND ALLOWING THEIR REMOVAL


def standarddeviationbelow(df, min, max, mean, std):
    # while loop here acts as an error trap, this is here if the user does not enter one of the required inputs
    while True:
        # if the smallest  protein length is more than 1 std below the mean, the following will occur:
        if min < (mean - std):
            print("\nMINIMUM LENGTH SEQUENCE IS >1 STD BELOW THE MEAN\n")			
            print('\n\t-Choice-\t-Action-')
            print('\t0\t:\t[DO NOT REMOVE]    any sequences')
            stdbelowcheck = mean
            n = 1
            # another while loop which looks for sequences with std below the mean
            # with each time this loop goes around the number of stds will increases, unless zero standard deviations are found or if it reaches the value of 5
            while stdbelowcheck > min and n <= 5:
                stdbelowcheck = mean - std*n
                stdbelow = df[df.apply( lambda x : x['Prot Length'] < (mean - std*n), axis=1 )].shape[0]
                if stdbelow == 0:
                    break
                print('\t%s\t:\t[REMOVE SEQUENCES] %s Sequences     that are     %s Standard Deviations below the Mean' % (n, stdbelow, n))
                totalbelow = n
                n += 1
            # the user will be faced with a decision based on information obtained from the above commands
            # the user will be asked to provide the script with a digit
            choice = input('\nplease input a digit of your choosing, the sequences to be removed will be displayed after your choice has been made\n').strip()
            # a list containing options for the user must is created
            b = range(0, totalbelow + 1)
            stdbelowlist = list(map(str, b))
            # the list is referenced to the user to check if the user input was valid
            check = any(item in choice for item in stdbelowlist)
            if check == True:
                # the input of the user determines the number of sequences that the user wants to remove
                # if the input is 0, the following will occur
                if choice == "0":
                    print('\n')
                    return df
                # if the user input is not 0, the actual number of stds below the mean have been inputted by the user
                # the user input must be converted into an integer
                else:
                    choice = int(choice)
                    # the script will then go on to locate the sequence that need to be removed
                    # once these sequence have been identified they are saved into a new dataframe, once this has occured the index is reset
                    stdbelowremove = df[df.apply( lambda x : x['Prot Length'] < (mean - std*choice), axis=1 )]
                    stdbelowremove1 = stdbelowremove.reset_index(drop=True, inplace=True)
                    # these particular sequences are now to be removed from the dataframe and saved to a new one
                    newdf = df[~df.apply( lambda x : x['Prot Length'] < (mean - std*choice), axis=1 )]
                    print('\n')
                    # the dataframe containing the sequences that are to be removed is displayed to the user
                    # the user is asked if they are happy with the removal of these sequences
                    print(stdbelowremove)
                    choices = input('\nyou have chosen for these sequences to be removed from the dataframe, are you happy with this decision? y/n\n').strip().lower()
                    ## if the user is happy with their decision and inputs y, the datafram is saved with the selected sequences removed, the function ends
                    if choices == "y":
                        print('\n')
                        return newdf
                    # if the user is not happy with their decision and inputs n, the function will restart
                    elif choices == "n":
                        print('\nlets try that again, please select the sequences to be removed again\n')
                    else:
                        print('\nINVALID INPUT PLEASE TRY AGAIN')
            else:
                print('\n')
                print('INVALID INPUT, PLEASE TRY AGAIN')

###### UPDATING THE DATAFRAME AND DISPLAYING THE NEW DATAFRAME TO THE USER
def updatedataframe (df, idlist, protchoice, home_dir, moment):
    # function will starting my counting the number of sequences and also the number of unique species within the dataframe
    total = df.shape[0]
    unique = len(df.drop_duplicates('Species Name'))
    # function will then create a list containing the different species within the dataframe
    specieslist = df['Species Name'].tolist()
    # the function will now display a summary of the info within the dataframe
    print('\n')
    print('A summary of the search results are displayed below:\n\nTaxon          :   %s\nProtein Family :   %s\nTotal sequences:   %s\nNo. of Species :   %s' % (idlist[0], protchoice, total, unique))
    # the function will then go on to create a dictionary of species : sequence counts
    numberoffasta = dict((x, specieslist.count(x)) for x in set(specieslist))
    print('\n')
    # function will then procede to show the user the 3 species with the highest number of sequences
    highestkey = sorted(numberoffasta, key=numberoffasta.get, reverse=True)[:3]
    highestvalue = []
    for item in highestkey:
        value = numberoffasta.get(item)
        highestvalue.append(value)
    print('\nSpecies: %-40s Sequences: %s\nSpecies: %-40s Sequences: %s\nSpecies: %-40s Sequences: %s\n' % (highestkey[0], highestvalue[0], highestkey[1], highestvalue[1], highestkey[2], highestvalue[1]))
    print('\n')
    print('The results contain redundant sequences.\nFASTA sequences will be downloaded later, and redundant sequences will be removed.')
    print('\n')
    # the function will ask the user if they want to view the list of species and the number of sequences for each species
    view = input('\nWould you like to view the full list of species and their respective number of FASTA sequences? y/n\n')
    if view == "y":
        # if the user decides that they want the view the list of species and their number of fasta sequences and inputs y, the following loop will occur
        for key, value in numberoffasta.items():
            print('Species: %-40s' 'Number of FASTA sequences: %s' %(key, numberoffasta[key]))
    # the function will then go on to ask the user if they wish to procede with the analysis
    choicex = 'empty'
    while True:
        choice = input('\ndo you want to procede with the analysis of this set of data? y/n\n').strip().lower()
        if choice == "y":
            return choicex, moment
        # the user may not want to go ahead with the analysis of this data set, if this is the case the user will be given some options of datasets to procede with 
        elif choice == "n":
            choicex = input('\n\n\nWhich set of data would you like to analyse??\n\n\t1 : Start again, change TaxID and Protein\n\t2 : Revert to dataset before removal of sequences standarded deviations that are above/below mean\n\nPlease input one of the digits above\n').strip()
            # if the user inputs 1, the following will occur:
            if choicex == "1":
                # the main output foler will be deleted and the users choice of data set will be displayed to them
                subprocess.call("rm -fr %s/Assignment2_%s" % (home_dir, moment), shell=True)
                print('lets try this again!')
                return choicex, moment
            # if the user inputs 2, the following will	occur:
            elif choicex == "2":
                print('\nthe script will procede with analysis on the set of data containing the sequences whose standard deviations are considerably above or below the mean')
                return choicex, moment
            else:
                ('\nINVALID INPUT, PLEASE INPUT EITHER 1 OR 2')
        else:
            print('\nINVALID INPUT, PLEASE TRY AGAIN')

# FUNCTION WHICH RUNS ALL FUNCTIONS


def runallfunctions():
    taxonidlist, home_dir = gettaxonid()
    newidlist = checktaxid(taxonidlist)
    protein = getprotein(newidlist)
    workpath = getworkpath()
    checkprotein, specieslist, genename, df = checkseq(newidlist, protein, home_dir, workpath)
    newprot, updatedidlist, newgene, df1, workpath = change (newidlist, protein, genename, home_dir, df, workpath)
    def stdfunctions (workpath):
        min, max, means, stds = checkingstandarddeviation(df1)
        df2 = standarddeviationabove (df1, min, max, means, stds)
        df3 = standarddeviationbelow(df2, min, max, means, stds)
        resetchoice, workpath =  updatedataframe (df3, updatedidlist, newprot, home_dir, workpath)
        if resetchoice == "1":
            return runallfunctions()
        elif resetchoice == "2":
            min, max, means, stds, df3, resetchoice, workpath = stdfunctions(workpath)
        return min, max, means, stds, df3, resetchoice, workpath
    parameters = stdfunctions(workpath)

runallfunctions()