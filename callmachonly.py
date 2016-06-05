import re, os, glob, subprocess

 
# get current working dir
WORK_DIR = os.getcwd()
#########################################################################
# PARAMETERS, I.E. INPUTS TO KNIFE CALL; need to add these here
#########################################################################

# dataset_name CANNOT HAVE ANY SPACES IN IT
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--dataset", help="name of dataset-NO SPACES- will be used for naming files")
# Should fix this later: not so good, no time now; get rid of dataset argument
# and search for dataset name, then add in run_id so as to differentiate runs
parser.add_argument("--knifeoutputtarball", help="path to tarred and zipped file of knife output directory, the tarball should unpack with the name of the directory the same as the dataset name")


args = parser.parse_args()
if args.dataset:
    dataset_name = args.dataset
else:
    dataset_name = "noname"

knife_output_tarball = args.knifeoutputtarball
    

    
# e.g. dataset_name = "4ep18" 

report_directory_name = "circReads"


# mode = "skipDenovo"
# read_id_style= "complete"
# junction_overlap =  8
# ntrim= 40

# Not really used, just doing so it mimics test Data call
# logstdout_from_knife = "logofstdoutfromknife"


logfile = WORK_DIR + "/logmachonly" + dataset_name + ".txt"

with open(logfile, 'w') as ff:
    ff.write(WORK_DIR)
    ff.write('\n\n\n')

    
# main directory to be used when running the knife:
knifedir = "/srv/software/knife/circularRNApipeline_Standalone"

#########################################################################
#
# tar and unpack the knife output directory
#   check that there is then a directory called dataset_name
#   this is a hack for now
#
#########################################################################

os.chdir(WORK_DIR)
with open(logfile, 'a') as ff:
    ff.write("\nAbout to try to unpack the tarfile " + knife_output_tarball + "\n")
try:
    fullcall = "tar -xvzf " + knife_output_tarball
    with open(logfile, 'a') as ff:
        subprocess.check_call(fullcall, stderr=ff, stdout = ff, shell=True)
except:
    with open(logfile, 'a') as ff:
        ff.write("\nError in unpacking the tarfile " + knife_output_tarball + "\n")

datadir = os.path.join(WORK_DIR,dataset_name)
if not os.path.isdir(datadir):
    with open(logfile, 'a') as ff:
        ff.write('ERROR: no directory\n' + datadir + '\nMake sure input of dataset matches dataset folder name unpacked from tarball.\n All later work is suspect.\n')
        
        

#########################################################################
#
# Note: should have unpacked tar of knife output results before doing
#   next part.
#
#########################################################################


###Run MACHETE
#Nathaniel Watson
#05-26-2016 

CIRCPIPE_DIR = os.path.join(WORK_DIR,dataset_name)
if not os.path.isdir(CIRCPIPE_DIR):
    with open(logfile, 'a') as ff:
        ff.write('Problem: no directory\n' + CIRCPIPE_DIR + '\nMaking one.')
    os.mkdir(CIRCPIPE_DIR)
CIRCREF = os.path.join(WORK_DIR,dataset_name,report_directory_name,"index")
if not os.path.isdir(CIRCREF):
    with open(logfile, 'a') as ff:
        ff.write('No directory\n' + CIRCREF + '\nNot so surprising.\nMaking one.')
    os.mkdir(CIRCREF)
MACH_OUTPUT_DIR = os.path.join(WORK_DIR,"mach")
os.mkdir(MACH_OUTPUT_DIR)
EXONS = os.path.join(WORK_DIR,"HG19exons")
REG_INDEL_INDICES = os.path.join(WORK_DIR,"IndelIndices")
#REG_INDEL_INDICES = os.path.join(WORK_DIR,"toyIndelIndices") #test indices for faster runs



#########################################################################
#
# move reference libraries output by KNIFE to directory CIRC_REF that
#   contains hg19_genome, hg19_transcriptome, hg19_junctions_reg and
#   hg19_junctions_scrambled bowtie indices
#
#########################################################################
    
 
# first have to 
#   change file names and mv them to the right directories


# Input file names are in an unusual format so they are easy to select when doing a run on
#   seven bridges. They should start in the home directory, as copies, because
#   they are entered as stage inputs. They start with the prefix "infile"
#   Move them to the directory where MACHETE
#   expects them to be, then change their names.


# Should still be in working dir now, but in case not
os.chdir(WORK_DIR)

globpattern = "infile*"
matching_files = glob.glob(globpattern)
if (len(matching_files)>= 1):
    for thisfile in matching_files:
        fullpatholdfile = WORK_DIR + "/" + thisfile
        fullpathnewfile = CIRCREF + "/" + re.sub(pattern=prefix, repl="", string= thisfile)
        with open(logfile, 'a') as ff:
            ff.write('About to do mv '+ fullpatholdfile + ' ' + fullpathnewfile + '\n')
        with open(logfile, 'a') as ff:
            subprocess.check_call(["mv", fullpatholdfile, fullpathnewfile], stderr=ff, stdout=ff)


    
# cd into the knife directory
os.chdir(knifedir)

with open(logfile, 'a') as ff:
    ff.write('\n\n\n')
    ff.write('Listing files in knifedir ' + knifedir) 
    
with open(logfile, 'a') as ff:
    ff.write('\n\n\n')
    subprocess.check_call(["ls", "-R"], stdout=ff)
    ff.write('\n\n\n')
    

# # run test of knife
# # sh completeRun.sh READ_DIRECTORY complete OUTPUT_DIRECTORY testData 8 phred64 circReads 40 2>&1 | tee out.log

# try:
#     with open(logfile, 'a') as ff:
#         ff.write('\n\n\n')
#         # changing so as to remove calls to perl:
#         subprocess.check_call("sh completeRun.sh " + WORK_DIR + " " + read_id_style + " " + WORK_DIR + " " + dataset_name + " " + str(junction_overlap) + " " + mode + " " + report_directory_name + " " + str(ntrim) + " 2>&1 | tee " + logstdout_from_knife , stdout = ff, shell=True)
#         # original test call:
#         # subprocess.check_call("sh completeRun.sh " + WORK_DIR + " complete " + WORK_DIR + " testData 8 phred64 circReads 40 2>&1 | tee outknifelog.txt", stdout = ff, shell=True)
# except:
#     with open(logfile, 'a') as ff:
#         ff.write('Error in running completeRun.sh')



# datadirlocation = WORK_DIR + "/" + dataset_name  

#############################################################################
#
# Now run the machete
#
#############################################################################




MACH_DIR = "/srv/software/machete"
MACH_RUN_SCRIPT = os.path.join(MACH_DIR,"run.py")

cmd = "python {MACH_RUN_SCRIPT} --circpipe-dir {CIRCPIPE_DIR} --output-dir {MACH_OUTPUT_DIR} --hg19Exons {EXONS} --reg-indel-indices {REG_INDEL_INDICES} --circref-dir {CIRCREF}".format(MACH_RUN_SCRIPT=MACH_RUN_SCRIPT,CIRCPIPE_DIR=CIRCPIPE_DIR,MACH_OUTPUT_DIR=MACH_OUTPUT_DIR,EXONS=EXONS,REG_INDEL_INDICES=REG_INDEL_INDICES,CIRCREF=CIRCREF)

with open(logfile, 'a') as ff:
        ff.write('\n\n\nAbout to run run.py\n')
        ff.write('\n\n\n')

with open(logfile, 'a') as ff:
        popen = subprocess.check_call(cmd,shell=True, stdout=ff, stderr=ff)




        


os.chdir(MACH_OUTPUT_DIR)

with open(logfile, 'a') as ff:
    ff.write('\n\n\nListing machete ouput directory\n\n\n')
    
with open(logfile, 'a') as ff:
    subprocess.check_call("ls -alRh", stdout=ff, stderr=ff, shell=True)
    
with open(logfile, 'a') as ff:
    ff.write('\n\n\nMasterError.txt should start here.\n\n\n')

os.chdir(WORK_DIR)
    
fullpatholderrorfile = MACH_OUTPUT_DIR + "/MasterError.txt"
if os.path.isfile(fullpatholderrorfile):
    subprocess.check_call("cat " + fullpatholderrorfile + " >> " + logfile, shell=True)
else:
    with open(logfile, 'a') as ff:
        ff.write('\n\n\nNo MasterError.txt file found.\n\n\n')

# tar everything in mach_output_dir/reports? Don't know if it exists yet, so
#   tar if it exists
os.chdir(WORK_DIR)
mach_output_reports_dir = os.path.join(MACH_OUTPUT_DIR,"reports")
if os.path.isdir(mach_output_reports_dir):
    try:
        fullcall = "tar -cvzf " + dataset_name + "machreports.tar.gz -C " + MACH_OUTPUT_DIR + " reports"  
        with open(logfile, 'a') as ff:
            subprocess.check_call(fullcall, stderr=ff, stdout = ff, shell=True)
    except:
        with open(logfile, 'a') as ff:
            ff.write("\nError in tarring the machete output report files in the " + mach_output_reports_dir + " directory\n")
else:
    with open(logfile, 'a') as ff:
        ff.write("\nNo directory of machete output report called " + mach_output_reports_dir + ", which was expected.\n")
    





        
