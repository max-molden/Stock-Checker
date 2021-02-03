# a web scraping bot to check the availability of the GeForce RTX 3070
# different urls for different sites and models

import requests as rq # access pages
from bs4 import BeautifulSoup # web scraping
import datetime # for time and date info
from pytz import reference # for time zone
import time # to track elapsed time of program

# unicode characters to help make it clear if somehting is in or out of stock
# for now leave them global, it is very difficult to get them to print correctly if storing in a list or a dict
checkmark = "\u2714 " # checkmark
red_x = "\u274C " # red heavy X
yellow_star = "\u2B50" # yellow star
dollar_sign = "\U0001F4B2" # green heavy dollar sign
dot = "\U0001F535" # white circle
yellow_bolt = "\u26A1"

# specifically works for newegg as the HTML tags may be (and most likely are) different for different sites
# a function to check if the item at the passed in url is in stock
# Input: url (the specific url for an item; after it is clicked on not on the search page)
# Processing: use requests and BeautifulSoup to get specific webpage info and check stock availability, then set a stock_bool var appropriately
# Output: a stock_bool either T/F or an error message if somehting is weird
def checkOnUrlNewegg(url):
    # T/F value for if the item is in stock or not
    stock_bool = None

    # get the webpage with requests and make a soup from it with BeautifulSoup
    webpage = rq.get(url)
    soup = BeautifulSoup(webpage.content, "lxml")

    # find the specific span tag with class availability and get its text
    stock_str = soup.find("span", class_ = "availability").get_text()

    # if out of stock set to false, in stock set to true, otherwise (if something unexpected) set to error message and return
    if stock_str == "OutOfStock":
        stock_bool == False
    elif stock_str == "InStock":
        stock_bool = True
    else:
        stock_bool = "ERROR: Could not get stock information, please check webpage and url; Try again."
        return stock_bool

    return stock_bool

def checkOnUrlEBay(url):
    # str to store the price of the listing, dont need it as number
    list_price = ""

    # try and scrape the link, since it is ebay the auction might end and there will be an error, in this case go to the except block
    try:
        # get the webpage with requests and make a soup from it with BeautifulSoup
        webpage = rq.get(url)
        soup = BeautifulSoup(webpage.content, "lxml")

        # find the specific div tag with class display-price and get its text
        list_price = soup.find("span", class_ = "notranslate").get_text()

        return list_price

    # if this block is hit there was some error with the link provided, most likekly that the auction eneded and an error will be returned so it can be accurately reflected in the output file
    except: 
        return "error"
        

# a function to display whether or not a specific listing is in stock, provides link for easy copy/paste if want
# Input: stock_bool (T/F item in stock or not), url(link to site for ease of access), description (simple description of brand and anything else before RTX 3070, plus that as well), output_file (the file to be written to)
# Processing: super simple if/else using the stock_bool as condition for the if.  If in stock display checkmark and delimeter (globals).  Both display the 
#   Else display X mark.  Both display whether item is or is NOT ins tock along with a link underneath for ease of access
# Output: writes to a file the information provided in a formatted manner
def displayStock(stock_bool, url, description, output_file):
    if stock_bool:
        output_file.write(f"{yellow_star*20}\n{checkmark}The {description} is in stock.\n\t\tLink: {url}\n{yellow_star*20}\n\n")
    else:
        output_file.write(f"{red_x}The {description} is NOT in stock.\n\t\tLink: {url}\n\n")

# a function to display the price of a specific listing on eBay
# Input: price (float from web scraping ebay func), url (link to site for ease of access), description (simple description of brand and anything else before RTX 3070, plus that as well), output_file (the file to be written to)
# Processing: just literally plugs all the info into an f-string
# Output: writes to a file the information provided in a formatted manner
def displayPrice(price, url, description, output_file):
    if price == "error":
        output_file.write(f"{yellow_bolt*5} There was a problem with this eBay link.  Please check the link and/or auction status. {yellow_bolt*5}\n\n")
    else:
        output_file.write(f"{dollar_sign*2} The {description} is listed at {price}.\n\t\tLink: {url}\n\n")


# Input: a .txt file that contains urls, item descriptions; both strs, separated by comma
# Processing: read the file, get all the data, format the data
# Output: an array containing the file info
def readInFile(infile_name, file_type):
    # open with read capabilites a .txt file to read in information to process
    input_file = open(infile_name, "r")

    # read all info from file, each line as a string ina list
    lines = input_file.readlines()

    #  need empty array to hold file info
    infos = []

    # reading in the lines of the file containig url and descriptor
    for line in lines:
        infos.append(line.split(","))

    if file_type == "input": # don't want to do this when reading the unicode file
        # removing \n newline character at the end of the product descriptor
        for i in range(0, len(infos)):
            infos[i][2] = infos[i][2].rstrip()

    return infos

def createOutFile(outfilename, mode):
    # open with write (overwrite) capabilities a .txt file to store output
    # the file is UTF-8 encoded so that I can use unicode characters, an X and a check to highlight in/out of stock
    output_file = open(outfilename, mode, encoding = "UTF-8")

    return output_file

def prepOutFile(output_file, type):
     # get current date and time at runtime of program
    now = datetime.datetime.now()
    # for time zone
    localtime = reference.LocalTimezone()

    # format the date, there are two commented out options, not sure which I like the best
    # now = now.strftime("%Y-%m-%d %H:%M:%S\n\n")
    # now = now.strftime("It is currently:\n\tDate: %m-%d-%Y\n\tTime: %H:%M:%S\n\n")
    # now = now.strftime("It is currently:\n\tDate: %b %d, %Y\n\tTime: %I:%M %p\n\n")

    if type == "output":
        now = now.strftime("It is currently:\n\tDate: %b %d, %Y\n\tTime: %I:%M %p " + localtime.tzname(now) + "\n\n")
    elif type == "times":
        now = now.strftime("Date: %b %d, %Y\nTime: %I:%M %p " + reference.LocalTimezone().tzname(datetime.datetime.now()))

    # try and print the time zone too
    # mostly bc I normally keep my laptop on EST no matter what, even if I am home in MST

    # printing time at top file
    output_file.write(f"{now}")

def main():
    # start the clock
    start = time.time()

    # file to store run times
    time_file_name = "3070availabilitytimes.txt"
    time_output_type = "times"
    time_output_mode = "a"
    time_output_file = createOutFile(time_file_name, time_output_mode)
    prepOutFile(time_output_file, time_output_type)

    # name and read the input file
    infile_name = "3070info.txt"
    infile_type = "input"
    # infile_mode = 
    infos = readInFile(infile_name, infile_type)

    # name, create, and prep (initial info) the output file
    outfilename = "3070availability.txt"
    output_type = "output"
    output_mode = "w"
    output_file = createOutFile(outfilename, output_mode)
    prepOutFile(output_file, output_type)

    # vars to help with printing respective site names, false if we haven't printed, true if have
    #   i.e. it will check if we have printed "new egg sites" and if it has then it will not print it agian, then will print best buy listings, etc.
    newegg_bool = False
    ebay_bool = False

    # to keep track of the current link number
    link_counter = 1

    # go over all the row info, passing, respectively, the correct info to the displayStock() and checkonURLxxx() funcs
    for row in range(0, len(infos)):
        if infos[row][0] == "newegg": # if it is a newegg site, indicated by first elem of line, call appropriate func
            if not newegg_bool:
                output_file.write(f"NEWEGG LISTINGS {dot*60}\n\n")
                newegg_bool = not newegg_bool
            output_file.write(str(link_counter) + ".\t")
            # calls displayStock(checkonUrlNewegg(url), url, descriptor) since infos is a 2D array where each element is an array containig the sitename, url, and the descriptor as its 3 elements
            displayStock(checkOnUrlNewegg(infos[row][1]),  infos[row][1], infos[row][2], output_file)
        elif infos[row][0] == "ebay": # if it is an ebay site, I want to list the price
            if not ebay_bool:
                output_file.write(f"EBAY LISTINGS {dot*61}\n\n")
                ebay_bool = not ebay_bool
            output_file.write(str(link_counter) + ".\t")
            displayPrice(checkOnUrlEBay(infos[row][1]), infos[row][1], infos[row][2], output_file)
        link_counter += 1
    # total amount of links, just for more stats, printed only to the time file
    time_output_file.write(f"\nNumber of Links Scraped: {len(infos)}")

    # total time it takes to run, must be before closing the file so I can write to it
    elapsed = time.time() - start

    # write time to the end of the output file and also add it to the time file...
    output_file.write(f"Elapsed Time = {elapsed:.4f}s.")

    # ... and also to the time file both to 4 decimal places
    time_output_file.write(f"\nElapsed Time: {elapsed:.4f}s\n\n")

    # close file just to be safe, good practice
    output_file.close()

if __name__ == "__main__":
    main()