# Reputation_check
This program provides getting reputation from some reputation sites. If you would like to check reputations of many FQDNs or IPs, 
this program helps you to get reputations automatically.<br>

## Reputation sites:
Reputation sites are below:
 - Symantec site review(https://sitereview.bluecoat.com/#/)
 - URL void(https://www.urlvoid.com/)
 - IP void(https://www.ipvoid.com/ip-blacklist-check/)

## Rreparation
You should install python and below libraries before starting the program in your PC.
 - Requests
 - Selenium

## Usage:
1. Download Reputation_check programs.
2. Open Reputation_check.py.
3. Change input file name and output filename. Program variable names are below:
   - INPUT_FILE
   - OUTPUT_FILE
   - OUTPUT_TMP_FILE
4. Make list of FQDNs and IPs, which you would like to check reputations.
   <br>Notes: You can add only FQDNs and IPs, you cannot add URLs.
5. Change name of the list to the input file name defined in INPUT_FILE.
6. Run Reputation_check.py which is main program.
