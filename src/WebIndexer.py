#!/usr/bin/env python

"""ReuterIndexer.py

Parses and indexes a folder of *.sgm files using SPIMI algorithm

Marc-Andre Faucher (9614729)
ma.faucher@gmail.com
"""

import re, csv, hashlib, os.path
import Tokeniser as tk
import InvertedIndex as ii

encoding = "iso-8859-1"

# From effbot.org/zone/re-sub.htm
def strip_html(text):
    def fixup(m):
        text = m.group(0)
        if text[:1] == "<":
            return "" # ignore tags
        if text[:2] == "&#":
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        elif text[:1] == "&":
            import htmlentitydefs
            entity = htmlentitydefs.entitydefs.get(text[1:-1])
            if entity:
                if entity[:2] == "&#":
                    try:
                        return unichr(int(entity[2:-1]))
                    except ValueError:
                        pass
                else:
                    return unicode(entity, "iso-8859-1")
        return text # leave as is
    return re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)

def allIndex(folder):
    result = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file == "index.html":
                result.append(root+"/"+file)
    return result

# I/O

def save(savefile, docList):
    """ Saves the document length information as a CSV
    Inspired by: http://www.doughellmann.com/PyMOTW/csv/#using-field-names
    """
    try:
        f = open(savefile, 'wb')
        fields = ('docId', 'docLength')
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writerow(dict((n,n) for n in fields))
        for key in docList:
            writer.writerow( { fields[0]:key, fields[1]:docList[key] } )
    finally:
        f.close()

def load(loadfile, docList):
    """ loads the document length information from a CSV
    Inspired by: http://www.doughellmann.com/PyMOTW/csv/#using-field-names
    """
    docList.clear()
    try:
        f = open(loadfile, 'rb')
        reader = csv.DictReader(f)
        for row in reader:
            docList[int(row['docId'])] = int(row['docLength'])
    finally:
        f.close()

class WebIndexer:
    fileList = []       # List of files to index
    checksums = []      # List of checksum to check for duplicates
    urls = {}           # Maps docId to urls
    docL = {}           # Maps docId to doc length
    block = 0           # Block size in number of files for SPIMI
    docId = 0           # Counter to keep track of current doc ID

    def __init__(self, folder='concordia.ca', blockSize=1):
        """ ReuterIndexer
        folder:     Folder of *.sgm files to parse
        blockSize:  Specify a block size for SPIMI in number of files
        """
        if blockSize > 1:
            self.block = blockSize
        else:
            self.block = 1
        self.fileList = allIndex(folder)

    def avgL(self):
        l = 0
        for docId in self.docL:
            l += self.docL[docId]
        return float(l) / float( len(self.docL) )

    def uniqueChecksum(self, string):
        string = string.encode("utf8")
        newChecksum = hashlib.md5(string).digest()
        for checksum in self.checksums:
            if newChecksum == checksum:
                print "Ignoring duplicate"
                return False
        self.checksums.append(newChecksum)
        return True

    def parse(self, doc, index, tokeniser):
        """ Parse a single file and add to InvertedIndex """
        try:
            f = open(doc, 'rb')
            
            regexBody = re.compile(r'(?<=<body)(?:.*?>)(.*)(?=</body>)', flags=(re.DOTALL|re.IGNORECASE))
            regexScript = re.compile(r'<script.*?<\/script>', flags=re.DOTALL)
            
            # Decode and filter files without body
            txt = f.read().decode(encoding)
            result = regexBody.findall(txt)
            if not result:
                return 0
            body = result[0]
            
            # Check for duplicates
            if not self.uniqueChecksum(body):
                return 0

            # Remove scripts, strip tags and convert special characters
            body = regexScript.sub('', body)
            body = strip_html(body)

            # Tokenise
            terms = tokeniser.tokenise(body)

            # Record length of document
            self.docL
            self.docL[self.docId] = len(terms)

            # Add terms to inverted index
            for term in terms:
                index[term] = self.docId
            self.urls[self.docId] = doc
            self.docId += 1
        finally:
            f.close()
    
    def spimi(self, index, tokeniser=None):
        """ Implements SPIMI index construction algorithm """
        if tokeniser is None:
            tokeniser = tk.Tokeniser()
        numberofblocks = ( len(self.fileList) + self.block - 1 ) // self.block
        if numberofblocks < 1:
            numberofblocks = 1
        for n in range( numberofblocks ):
            index.clear()
            print "Parsing Block " + str(n) + "... "
            for doc in self.fileList[n*self.block: (n * self.block) + self.block]:
                self.parse(doc, index, tokeniser)
            ii.save("index/index"+str(n)+".csv", index)
        print "Merging... "
        ii.mergeFile( "index/fullindex.csv", [ "index/index"+str(n)+".csv" for n in range(numberofblocks) ] )
        save('index/doclength.csv', self.docL)

    def display(self, docId):
        try:
            f = open(self.urls[docId], 'rb')
            
            regexBody = re.compile(r'(?<=<body)(?:.*?>)(.*)(?=</body>)', flags=(re.DOTALL|re.IGNORECASE))
            regexScript = re.compile(r'<script.*?<\/script>', flags=re.DOTALL)
            
            # Decode and find body
            txt = f.read().decode(encoding)
            body = regexBody.findall(txt)[0]
            
            # Remove scripts, strip tags and convert special characters
            body = regexScript.sub('', body)
            body = strip_html(body)

            print self.urls[docId]
            print body
        finally:
            f.close()