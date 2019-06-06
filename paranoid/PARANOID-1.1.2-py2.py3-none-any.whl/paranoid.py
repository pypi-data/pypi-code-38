#! /usr/bin/env python
import os
import logging
import io
from os import listdir
from os.path import isfile, join
import random
import string
import argparse
import re
import sys
from datetime import datetime
from time import gmtime, strftime




if sys.version_info[0] < 3:  ##to check python version and modify for the code to run in python2 versions
    from io import open

    reload(sys)
    sys.setdefaultencoding('utf8')


def read_in_chunks(file_object,chunk_size=2000):  # reads the file in chunks of default 2000 bytes this can be specified by users
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def timeStampVaalidator(word):
    new_word = word.strip()
    obj = re.match("^([0-9]{2,4})\/([0-1][0-9])\/([0-3][0-9])(?:( [0-2][0-9]):([0-5][0-9]):([0-5][0-9]))?$", new_word,
                   re.M | re.I)
    obj1 = re.match("^([0-9]{2,4})-([0-1][0-9])-([0-3][0-9])(?:( [0-2][0-9]):([0-5][0-9]):([0-5][0-9]))?$", new_word,
                    re.M | re.I)
    obj2 = re.match("^([0-3][0-9])-([0-1][0-9])-([0-9]{2,4})(?:( [0-2][0-9]):([0-5][0-9]):([0-5][0-9]))?$", new_word,
                    re.M | re.I)
    obj3 = re.match("^([0-3][0-9])\/([0-1][0-9])\/([0-9]{2,4})(?:( [0-2][0-9]):([0-5][0-9]):([0-5][0-9]))?$", new_word,
                    re.M | re.I)
    obj4 = re.match("^([0-3][0-9])\.([0-1][0-9])\.([0-9]{2,4})(?:( [0-2][0-9]):([0-5][0-9]):([0-5][0-9]))?$", new_word,
                    re.M | re.I)
    obj5 = re.match("^([0-9]{2,4})\.([0-1][0-9])\.([0-3][0-9])(?:([0-2][0-9]):([0-5][0-9]):([0-5][0-9]))?$", new_word,
                    re.M | re.I)
    obj6 = re.match("(([0-9]{2,4})-([0-1][0-9]|[0-9])-[0-3][0-9]T)(?:([0-2][0-9]):([0-5][0-9]):([0-5][0-9]))?$",
                    new_word, re.M | re.I)

    if obj:
        time = strftime("%Y/%m/%d %H:%M:%S", gmtime()).split(' ')
        return True, time[0]
    elif obj1:
        time = (str(datetime.now()).split(' '))
        return True, time[0]
    elif obj2:
        time = strftime("%d-%m-%Y %H:%M:%S", gmtime()).split(' ')
        return True, time[0]
    elif obj3:
        time = strftime("%d/%m/%Y %H:%M:%S", gmtime()).split(' ')
        return True, time[0]

    elif obj4:
        time = strftime("%d.%m.%Y %H:%M:%S", gmtime()).split(' ')
        return True, time[0]
    elif obj5:
        time = datetime.today().isoformat()
        return True, time
    elif obj6:
        time = datetime.today().isoformat()
        return True, time

    else:
        return False, word


def maskGenerator(word, flag=False):  # iterates through word letter by letter and replaces the same by random character
    c = ""
    r, f = timeStampVaalidator(word)
    if r:  # checking if it is a time stamp
        return f
    else:  # if not iterating through each element and masking it
        i = 0

        if "[CDATA" in word:
              word = word.replace("[CDATA", "***")


        while (i < len(word)):
            if word[i].isdigit():
                c += str(random.randint(1, 9))
            elif word[i].isupper():
                c += random.choice(string.ascii_letters).upper()
            elif word[i].isspace():
                c = c + word[i]
            elif word[i].islower():
                c += random.choice(string.ascii_letters).lower()
            else:
                if flag == True:
                    if word[i] == "&":
                        while word[i] != ";":
                            c += word[i]
                            i += 1
                        c = c + ';'
                    else:
                        c += word[i]
                else:
                    c += word[i]
            i += 1

        c = c.replace("***", "[CDATA")
        return c


def xmlTagMask(s):  # masks the xml attributes

    # exception for the xml header tag
    mask = True
    if "xsi" in s:
        return s
    elif "Namespace" in s:
        return s
    elif "<?" in s:
        return s


    # masking xml attributes

    if ("=" in s) and ("\"" in s):
        y = ""
        i = 0
        while (i < len(s)):
            if s[i] == "=":
                c = 0
                while c < 2:
                    y = y + maskGenerator(s[i])
                    i += 1
                    if s[i] == ("\""):
                        c += 1

            y = y + s[i]
            i += 1
        return y

    else:
        return s


def xmlSpecificTagMask(s, masked,tag_mask_flag,userInput=[], xpath=""):
    flag = False
    if "<?" in s:
        return xmlTagMask(s), True, xpath, masked
    elif "!--" in s:
        return xmlTagMask(s), True, xpath,masked
    else:
        xmlAttList = []
        att = "None"
        xmlTag = ""
        r = ""
        r = s.strip()

        if "=" in r:
            xmlAttList = r.split("=")
            xmlTag = xmlAttList[0].split(' ')[0]
            xmlTag = xmlTag[1:]
            if 'ns:' in xmlTag:
                x = xmlTag.split(":")
                xmlTag = x[1]


        else:
            xmlTag = r
            xmlTag = r[1:]
            if 'ns:' in xmlTag:
                x = xmlTag.split(":")
                xmlTag = x[1]

        if xpath == "" or xpath == None:

            xpath = "/" + xmlTag
        else:
            if xmlTag != None:
                xpath = xpath + "/" + xmlTag
        if(len(userInput) > 0):
            for i in userInput:
                 if ((i == xpath)):
                     if tag_mask_flag:
                            masked += 1
                     return xmlTagMask(s), True, xpath,masked
        else:
            return xmlTagMask(s), True, xpath, masked

        return s, False, xpath, masked


def xpathModification(xpath, endTag,tag_count):
    if xpath == "":
        return ""

    if 'ns:' in endTag:
        x = endTag.split(":")
        endTag = "/"+x[1]

    endTag = endTag.strip()
    xpathList = xpath.split("/")
    if xpathList[-1] == endTag[1:]:
        del xpathList[-1]
        tag_count = tag_count + 1

    c = "/"
    #print(xpathList)
    xpath = c.join(xpathList)
    #print(xpath)
    return xpath,tag_count


def jsonmaskgenerator(s):  # function to mask json content

    if ":" not in s:  # checking for : sign
        return s

    if ("}" in s) or ("]" in s):
        c = 0
        r = ""
        i = 0

        while ((s[i] != "}") or (s[
                                     i] != "]")):  # iterating and appending the content of the xml attribure and then performing slicing to mask the content


            r = r + s[i]
            c += 1
            i += 1
            if (i >= (len(s) - 1)):
                break

        k = r.split(':')
        s = s[c:]
        m = maskGenerator(k[1])


        return ":" + m + s

    else:
        m = s.split(':')
        ## fix 30th May 2019
        ## to handle when there are ":" in the contents as well
        if len(m) > 2:
            m = m[1:]
            k = ':'.join(m)
            c = []
            c.append('')
            c.append(k)
            m = c
            c = []
            k = ''
        ## end of fix
        n = maskGenerator((m[1]))
        return ":" + n





def xmlParse(input, out, bufferbyte, tag_count,masked,mask=""):
    listmask = []
    xpath = ""
    cdataList = []
    cdataInitial = False
    cdata = False
    cdataContent = ""
    mask = str(mask)
    tag_mask_flag  = True
    if ',' in mask:
        listmask = mask.split(',')
    elif mask == "" or mask == "None":
        listmask = []
    else:
        listmask.append(mask)

    if len(listmask) > 0:
        shouldMask = False
    else:
        shouldMask = True
    additional_content = ""  # to store the contents of the line if it is not ending with > tag
    with open(input, buffering=bufferbyte, encoding="utf-8") as file:
        for file_content in read_in_chunks(file, ((int(bufferbyte / 2)))):  # iterating through chunks of file

            flag = True  # to check wether we have opening tag in the content that is being read currently
            # file_content = file_content.strip()
            c = 0
            if additional_content != "":  # to check wether we have contents of the file that dows not end with >
                file_content = additional_content + file_content
                additional_content = ""
            if file_content.endswith('>'):
                file_content = file_content
                if '[CDATA' in file_content:
                    result = file_content.find('[CDATA')
                    cdataContent = file_content[result-2:]
                    file_content = file_content[:result-2]
                    cdataInitial = True

            else:
                additional_content = ""
                c = 0  # count to slice the string
                n = True  # to identify closing and opening tag
                if '<' in file_content:
                    for k in (reversed(file_content)):
                        if k == '<':
                            n = True
                            break
                        elif k == '>':
                            n = False
                            break
                        c = c + 1
                    if n == True:
                        additional_content = "<" + file_content[
                                                   (len(file_content) - c):]  # adding the contents of the last tag
                        file_content = file_content[0:(len(
                            file_content) - c - 1)]  # slicing the content that has been appendide in the additional_content variable
                    else:
                        additional_content = file_content[-c:]
                        file_content = file_content[0:((len(file_content)) - c)]

                    flag = True
                else:
                    additional_content = file_content
                    file_content = ""
                    flag = False

                if '[CDATA' in file_content:
                    result = file_content.find('[CDATA')
                    cdataContent = file_content[result-2:]
                    file_content = file_content[:result-2]
                    cdataInitial = True

            if flag == True and cdata == False:
                lines = file_content.split('>')
                with open(out, "a+", encoding="utf-8") as file2:
                    for i in lines:  # iterating through the lines
                        if (i.strip().startswith('<') and i.strip()[1] != "/"):

                            i, shouldMask, xpath,masked = xmlSpecificTagMask(i,masked,tag_mask_flag , listmask, xpath)  # masking xml atrribute

                            file2.write(i + ">")  # writing in the output file

                        else:
                            b = i.split("<")  # splitting based on opening tag
                            if (sys.version_info[
                                0] < 3):  # since below python 3 we do not have unicode characters by default.
                                if shouldMask == True:
                                    file2.write(maskGenerator(b[0], True).decode('utf-8'))  # masking the attributes

                                else:
                                    file2.write(b[0].decode('utf-8'))
                                if len(b) > 1:
                                    #Fix May19 issue reported by kris
                                    try:
                                        xpath,tag_count = xpathModification(xpath, xmlTagMask(b[1]),tag_count)
                                    except:
                                        xpathModification(xpath, xmlTagMask(b[1]),tag_count)
                                    #Fix complete
                                    file2.write("<" + xmlTagMask(b[1]) + ">")  # appending the closing tags

                            else:
                                if shouldMask == True:
                                    file2.write(maskGenerator(b[0], True))  # masking the attributes


                                else:
                                    file2.write(b[0])
                                if len(b) > 1:
                                    xpath,tag_count = xpathModification(xpath, xmlTagMask(b[1]),tag_count)

                                    file2.write("<" + xmlTagMask(b[1]) + ">")  # appending the closing tags



                cdata = cdataInitial


            if cdata == True:
                countIndex = 0
                lastIndex = 0
                with open(out, "a", encoding="utf-8") as file2:
                   for i in cdataContent:
                       if i == "[":
                           cdataList.append("[")
                       elif(i == "]"):
                           cdataList.pop()
                           lastIndex = countIndex
                       countIndex += 1

                   if len(cdataList) < 1:
                       if lastIndex != countIndex:
                           additional_content = cdataContent[lastIndex+2 :]
                           cdataContent = cdataContent[:lastIndex+2]
                       else:
                           cdataContent = cdataContent
                       cdata = False
                       cdataInitial = False
                       if (sys.version_info[0] < 3):  # since below python 3 we do not have unicode characters by default.
                               if shouldMask == True:
                                   file2.write(maskGenerator(cdataContent, True).decode('utf-8'))  # masking the attributes

                               else:
                                   file2.write(cdataContent.decode('utf-8'))

                       else:
                           if shouldMask == True:
                               file2.write(maskGenerator(cdataContent, True))  # masking the attributes

                           else:
                               file2.write(cdataContent)

            if additional_content != "":
                        lines = additional_content.split('>')
                        with open(out, "a", encoding="utf-8") as file2:
                            for i in lines:  # iterating through the lines
                                if (i.strip().startswith('<') and i.strip()[1] != "/"):
                                    i, shouldMask, xpath,masked = xmlSpecificTagMask(i,masked,tag_mask_flag, listmask, xpath)  # masking xml atrribute
                                    file2.write(i + ">")  # writing in the output file

                                else:
                                    b = i.split("<")  # splitting based on opening tag
                                    if (sys.version_info[
                                        0] < 3):  # since below python 3 we do not have unicode characters by default.
                                        if shouldMask == True:
                                            file2.write(maskGenerator(b[0], True).decode('utf-8'))  # masking the attributes


                                        else:
                                            file2.write(b[0].decode('utf-8'))

                                        if len(b) > 1:
                                            # fix for kris issue on may 19 2019
                                             try:
                                                 xpath,tag_count = xpathModification(xpath, xmlTagMask(b[1]),tag_count)
                                             except:
                                                xpathModification(xpath, xmlTagMask(b[1]),tag_count)
                                            #completed fix
                                             file2.write("<" + xmlTagMask(b[1]) + ">")  # appending the closing tags


                                    else:
                                        if shouldMask == True:
                                            file2.write(maskGenerator(b[0], True))  # masking the attributes


                                        else:
                                            file2.write(b[0])

                                        if len(b) > 1:
                                            xpath,tag_count = xpathModification(xpath, xmlTagMask(b[1]),tag_count)
                                            file2.write("<" + xmlTagMask(b[1]) + ">")  # appending the closing tags


            if(len(listmask) < 1):
                masked = tag_count



    return tag_count,masked


def jsonParse(input, out, bufferbyte):
    additiona_content = ""  # to store line not ending with :
    with open(input, buffering=bufferbyte, encoding="utf-8") as file:
        for content in read_in_chunks(file, (int(bufferbyte / 2))):

            if additiona_content != "":
                content = additiona_content + content  # adding remaining content to the new content
            if content[-1] == ':':
                content = content[:-1]
                additiona_content = ':'

            else:
                c = 0
                for k in reversed(content):
                    if k == ':':
                        break
                    c += 1
                additiona_content = content[-c - 1:]  # adding the contents till :
                content = content[
                          :-c - 1]  # removing the contents by slicing off the data present in additional content
                with open(out, "a+", encoding="utf-8") as file2:
                    i = 0
                    s = ""
                    while (i < len(content)):
                        if content[i] == ":":
                            r = ""
                            while (content[i] != ","):  # iterating through the data to mask
                                check = i  # #to change the value of i later on if the list has data instead of k,v pairs
                                flag = False
                                if content[i] == '[':  # to check wehter the list has key value pairs

                                    k = ""
                                    while content[check] != ']':

                                        if content[check] == '{':
                                            flag = True
                                            break
                                        else:
                                            k = k + maskGenerator(content[check])
                                            check += 1
                                    if flag == False:
                                        i = check + 1
                                        s = s + ":" + k + "]"
                                        r = ""
                                        #30th May Fix
                                        break
                                        #end

                                if flag == True or i < len(content):

                                    if content[i] == '{' or content[i] == '[':
                                        r = r + content[i]
                                        i = i + 1
                                        break

                                    else:
                                        # s = s + content[i]
                                        r = r + content[i]
                                        i = i + 1

                            if r != "":
                                if ('{' not in r) or ('[' not in r):
                                    s = s + jsonmaskgenerator(r)
                                else:
                                    s = s + r

                        else:
                            s = s + content[i]
                            i += 1

                    file2.write(s)

    with open(out, "a", encoding="utf-8") as file2:
        file2.write(jsonmaskgenerator(additiona_content))


def commandLine(args):
    file_count = 0
    if args.log != "":
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
            handlers=[
                logging.FileHandler(args.log),
                logging.StreamHandler()
            ])

    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
            handlers=[
                logging.StreamHandler()
            ])

    logger = logging.getLogger()



    if args.input != "":

        if (os.path.isdir(args.input)):
            inputDirectory = args.input + "/"
            if not os.path.exists(args.outputDir):
                try:
                    os.makedirs(args.outputDir)
                except:
                    logger.warning("Exiting no write access")
                    sys.exit()
            if not os.access(args.outputDir, os.W_OK):
                logger.warning('Exiting no write access')
                sys.exit()
            files = []
            logger.info("Initializing Masking")
            logger.info("Processing")
            for subdir, dirs, allfiles in os.walk(inputDirectory):
                for file in allfiles:
                    files.append(os.path.join(subdir, file))
            for names in files:
                tag_count = 0
                tag_mask = 0
                name, ext = os.path.splitext(names)
                fileName = name.split(inputDirectory)
                output = args.outputDir + "/" + fileName[-1] + ext
                if not os.path.exists(os.path.dirname(output)):
                    os.makedirs(os.path.dirname(output))
                if os.path.exists(output):
                    os.remove(output)


                if ext == ".xml":
                    tag_count,tag_mask = xmlParse((names), output, args.byteSize,tag_count ,tag_mask, args.mask)
                    logger.info("Completed Processing " + inputDirectory + names + " Maksed file location " + output)
                    logger.info("Total tags found in "+name + " = "+ str(tag_count))
                    logger.info("Total tags masked in  " + name + " = " + str(tag_mask))

                elif ext == ".json":
                    jsonParse((names), output, args.byteSize)
                    logger.info("Completed Processing " + names + " Maksed file location " + output)
                file_count += 1

            logger.info("Total files Masked "+str(file_count))







        elif os.path.isfile(args.input):
            tag_count = 0
            tag_mask = 0
            name, ext = os.path.splitext(args.input)
            fileName = name.split("/").pop()
            if not os.path.exists(args.outputDir):
                try:
                    os.makedirs(args.outputDir)
                except:
                    logger.warning("Exiting no write access")
                    sys.exit()
            if not os.access(args.outputDir, os.W_OK):
                logger.warning("Exiting no write access")
                sys.exit()
            output = args.outputDir + "/" + fileName + ext
            if os.path.exists(output):
                os.remove(output)

            logger.info("Initialising Masking")

            if ext == ".xml":
                tag_count,tag_mask = xmlParse(args.input, output, args.byteSize,tag_count,tag_mask, args.mask)
                logger.info("Completed Processing " + args.input + " Maksed file location " + output)
                logger.info("Total tags found in " + fileName + " = " + str(tag_count))
                logger.info("Total tags masked in  " + fileName + " = " + str(tag_mask))

            elif ext == ".json":
                logger.info("Processing " + fileName)
                jsonParse(args.input, output, args.byteSize)
                logger.info("Completed Processing " + args.input + " Maksed file location " + output)



            else:
                logger.warning("Please provide valid xml/json file")
                sys.exit()

            logger.info("Masking Completed")
        else:
            logger.warning("Invalid directory/ File ")
            sys.exit()

    else:
        logger.warning("Please provide input")
        sys.exit()


def main():
    parser = argparse.ArgumentParser(description="Data Masking")
    parser.add_argument("-i", help="Input Directory Name / File Name", dest="input", type=str, default="",
                        required=True)
    parser.add_argument("-b", help="Provide byte size to buffer", dest="byteSize", type=int, default="2000000")
    parser.add_argument("-o", help="Output Directory Name", dest="outputDir", type=str, required=True)
    parser.add_argument("-l", help="Input xpath or xpaths seperated by ,", dest="mask", type=str)
    parser.add_argument("-L", help="Output in Log File",dest="log", type=str,default="")
    parser.set_defaults(func=commandLine)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
