# a web scraping bot to check the availability of the GeForce RTX 3070
# different urls for different sites and models

import requests as rq 
from bs4 import BeautifulSoup
import datetime

# get current date and time at runtime of program
now = datetime.datetime.now()
# now = now.strftime("%Y-%m-%d %H:%M:%S\n\n")
now = now.strftime("It is currently:\n\tDate: %m-%d-%Y\n\tTime: %H:%M:%S\n\n")

# open with read capabilites a .txt file to read in information to process
# contains urls, item descriptions
# both strs, separated by comma
'''
ALWAYS MAKE SURE TO HIT ENTER AT THE END OF EACH LINE, INCLUDING THE LAST
OTHERWISE THERE WILL BE AN ISSUE WITH THE DESCRIPTION
THE LAST char OF THE DESCIRPTION IS REMOVED SINCE ALL EXCEPT THE LAST I HIT ENTER TO MAKE ANEW LINE
SO WE NEED A NEW LINE AT THE END OF THE FILE
i.e. CURSOR SHOULD BE ON AN EMPTY LINE AFTER THE FINAL ENTRY
'''
input_file = open("3070info.txt", "r")
lines = input_file.readlines()

# open with write (overwrite) capabilities a .txt file to store output
# the file is UTF-8 encoded so that I can use unicode characters, an X and a check to highlight in/out of stock
output_file = open("3070availability.txt", "w", encoding = "UTF-8")
output_file.write(f"{now}")

# unicode characters to help make it clear if somehting is in or out of stock
checkmark = "\u2714 " # checkmark
x_red = "\u274C " # red heavy X
star_yellow = "\u2B50" # yellow star

# a delimeter to make it even more clear when an item is in stock, will be used to surround the output to the .txt file
# delimeter = 20*"*"
delimeter = star_yellow*20

# specifically works for newegg as the HTML tags may be (and most likely are) different for different sites
# a function to check if the item at the passed in url is in stock
# Input: url (the specific url for an item; after it is clicked on not on the search page)
# Processing: use requests and BeautifulSoup to get specific webpage info and check stock availability, then set a stock_bool var appropriately
# Output: a stock_bool either T/F or an error message if somehting is weird
def checkOnURLNewegg(url):
    stock_bool = None # T/F value for if the item is in stock or not

    # get the webpage with requests and make a soup from it with BeautifulSoup
    webpage = rq.get(url)
    soup = BeautifulSoup(webpage.content, "lxml")

    # an empty string to store the string returned from the availability attribute of HTML
    #       the stock variable (or whatever IDK HTML) is in a <div> tag, then a <span> tag and is in the variable availability
    #               will either be OutOfStock or InStock
    stock_str = ""

    # check through all div tags, the specific one nosto_product is what we want, then get span tag with availability var, then get its value as as str
    for availability in soup.find_all("div", class_ = "nosto_product"):
        stock_str = availability.find("span", class_ = "availability")
        stock_str = stock_str.string

    # if out of stock set to false, in stock set to true, otherwise (if something unexpected) set to error message and return
    if stock_str == "OutOfStock":
        stock_bool == False
    elif stock_str == "InStock":
        stock_bool = True
    else:
        stock_bool = "ERROR: Could not get stock information, please check webpage and url; Try again."
        return stock_bool

    return stock_bool

# a function to display whether or not a specific listing is in stock, does not matter the website, provides link for easy copy/paste if want
# Input: stock_bool (T/F item in stock or not), url(link to site for ease of access), description (simple description of brand and anything else before RTX 3070, plus that as well)
# Processing: super simple if/else using the stock_bool as condition for the if.  If in stock display checkmark and delimeter (globals).  Both display the 
#   Else display X mark.  Both display whether item is or is NOT ins tock along with a link underneath for ease of access
def displayStock(stock_bool, url, description):
    if stock_bool:
        # print(f"\n{delimeter}\nThe {description} is in stock.\n\tLink: {url}\n{delimeter}")
        output_file.write(f"{delimeter}\n{checkmark}The {description} is in stock.\n\t\tLink: {url}\n{delimeter}\n\n")
    else:
        # print(f"\nThe {description} is NOT in stock.\n\tLink: {url}")
        output_file.write(f"{x_red}The {description} is NOT in stock.\n\t\tLink: {url}\n\n")


def main():
    #  need empty array to hold file info
    infos = []

    # reading in the lines of the file containig url and descriptor
    for line in lines:
        infos.append(line.split(","))
    # removing \n newline character at the end of the product descriptor
    for i in range(0, len(infos)):
        infos[i][2] = infos[i][2][:-1]

    for j in range(0, len(infos)):
        if infos[j][0] == "newegg": # if it is a newegg site, indicated by first elem of line, call appropriate func
            # calls displayStock(checkonURLNewegg(url), url, descriptor) since infos is a 2D array where each element is an array containig the sitename, url, and the descriptor as its 3 elements
            displayStock(checkOnURLNewegg(infos[j][1]),  infos[j][1], infos[j][2])
        else: # else it is anotehr site, call appropriate func
            pass


if __name__ == "__main__":
    main()
    output_file.close() # close file just to be safe, good practice

'''
put all urls and descriptions into a text file, separate them by a line where it says newegg, or another site later,
for now just use newegg i guess until i find another site to use
'''

'''
kinda clean up code
put file open/close for i/o files into a func, can be main, probs need to be becuase of globality?
put unicode in a file and read that in
'''