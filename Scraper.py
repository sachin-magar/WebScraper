
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
import csv

def getCategores(url,beautifulSoup_object):

    # mainCategory will have main category name as key and its link as value
    # subCategories will have sub category as key and its link as value
    # categoriesDictionary will have main category as key and list of subcategories as value
    mainCategories = {}
    subCategories = {}
    categoriesDictionary = {}
    previosMainCategory = None

    # Check for Categories, select the rows starting with tag span
    for categories in beautifulSoup_object.findAll("span"):

        # Attributes and their names are stored in a dictionary called attrs
        # Since we need only higher level categories we will filter the data on class
        try:
            if 'class' in categories.attrs:
                if categories.attrs['class'] == ['menu__title']:
                    # use header-tracking attribute to distinguish between main category and subcategory
                    if 'header-tracking' in categories.parent.attrs:
                        checkForMainCategory = categories.parent.attrs['header-tracking']
                    if checkForMainCategory is not None and checkForMainCategory == 'topics.category':

                        # whenever we will get a new main category append sub categories to previous category
                        # since we will get first category before sub categories, put an if to avoid exception
                        if previosMainCategory is not None:
                            categoriesDictionary[previosMainCategory] = subCategories

                        # Add current main category to all categories, reassign subcategories,
                        # make current main category as previosMainCategory
                        mainCategories[categories.text] = categories.parent.attrs['href']
                        subCategories = {}
                        previosMainCategory = categories.text
                    else:
                        subCategories[categories.text] = categories.parent.attrs['href']

        except Exception:
            print (Exception.__text_signature__)

    # return main categories and categories dictionary
    return (mainCategories,categoriesDictionary)


def getCompleteList(mainCategories,categoriesDictionary, url):

    # iterate through each category and save the list of books in a csv file
    for mainCategory in mainCategories.keys():

        # Write name of main category in output file
        with open("output.csv", "a",newline='') as file:
            writer = csv.writer(file)
            writer.writerow([])
            writer.writerow([mainCategory,""])


        for subCategory in categoriesDictionary[mainCategory].items():
            # add name of subcategory to output file
            with open("output.csv", "a",newline='') as file:
                writer = csv.writer(file)
                writer.writerow([])
                writer.writerow([mainCategory+" --> "+subCategory[0]])
                writer.writerow([" Course Name ", " Course Description "])


            # add url for all-courses in each category
            newURL = url + subCategory[1] + "all-courses/"
            baseURL = url + subCategory[1] + "all-courses/"

            # count is used to handle pagination
            pageCount = 1

            while (True):
                try:
                    # Use FireFox with selenium for getting dynamic content from web page
                    driver = webdriver.Firefox()
                    driver.get(newURL)
                    html = driver.page_source
                    beautifulSoup_object = BeautifulSoup(html, "html.parser")
                except Exception:
                    print("Void page")

                # Select content inside ui-view tag since books are listed in this tag
                ui_tag = beautifulSoup_object.find("ui-view")

                # Get book name and description from this tags a and p
                name = ui_tag.findAll("a", {"class": "card__title"})
                description = ui_tag.findAll("p", {"class": "card__subtitle"})

                for i in range(len(name)):
                    # print("name: ", name[i].text, " Description: ", description[i].text)
                    with open("output.csv", "a",newline='') as file:
                        try:
                            writer = csv.writer(file)
                            writer.writerow([name[i].text,description[i].text])

                        except Exception:
                            print ("Incompatible text format")

                # Break when we reach at the end of pagination else goto next page
                checkNextPage = ui_tag.find("li", {"ng-class": "{ disabled: !hasNext() }"})
                pageCount = pageCount + 1
                if "class" in checkNextPage.attrs:
                    break
                else:
                    newURL = baseURL + "?p=" + str(pageCount)


if __name__ == '__main__':
    # Define the URL for udemy
    url = "https://www.udemy.com/courses/"
    short_url = "https://www.udemy.com"

    # Get the data in html
    html = urlopen(url)

    # Get entire page in beautiful soup object
    beautifulSoup_object = BeautifulSoup(html,"html.parser")

    # call getCategories to get all main categories and its sub categories
    mainCategories, categoriesDictionary = getCategores(url, beautifulSoup_object )

    # call getCompleteList() to get entire list
    # getCompleteList(mainCategories,categoriesDictionary,short_url)

    # call getTestOutput to check for a sample list
    testMainCategories = {' Lifestyle ': '/courses/lifestyle/'}
    testCategoriesDictionary = {' Lifestyle ': {'Pet Care & Training': '/courses/lifestyle/pet-care-and-training/',
                                                'Home Improvement': '/courses/lifestyle/home-improvement/'} }

    # get output for sample list
    getCompleteList(testMainCategories,testCategoriesDictionary,short_url)

