#!/usr/bin/env python

from numpy import * #http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy
import math, random
import InvertedIndex as ii
import WebIndexer as wi

def vectorLength(v):
    return (sum(v**2.0))**0.5
    
def distance(v1, v2):
    return vectorLength(v1 - v2)

def termCount(terms):
    termDict = {}
    for term in terms:
        if term not in termDict:
            termDict[term] = 1
        else:
            termDict[term] += 1

class VectorSpace:
    index = None
    indexer = None
    vectorIndex = None
    numberOfTerms = 0
    numberOfDocs = 0
    
    def __init__(self, iIndex, iIndexer):
        self.index = iIndex
        self.indexer = iIndexer
        self.numberOfTerms = len(self.index)
        self.numberOfDocs = len(self.indexer.docL)
    
    def computeIDF(self, term):
        df = self.index.df(term)
        return math.log( (float(self.numberOfDocs)/df), 10 )

    def buildVectors(self):
        # iterate the index and swap 0 to tfidf where applicable
        #print "swapping 0s for real tfidf..."
        self.vectorIndex = zeros( (self.numberOfDocs, self.numberOfTerms) )
        pos = 0
        for term in self.index: #this gives "ball"
            idf = self.computeIDF(term)
            for entry in self.index[term]: #this gives [ [25, 1], [587, 6], .... ]
                self.vectorIndex[entry[0], pos] = entry[1]*idf
            pos += 1
            
    def buildQueryVector(self, terms):
        termDict = termCount(terms)
        vector = zeros( self.numberOfTerms )
        if not termDict:
            return vector
        pos = 0
        for term in self.index:
            if term in termDict:
                vector[pos] = termDict[term]*self.computeIDF(term)
            pos += 1
        return vector

    def length(self, vectorID):
        return vectorLength(self.vectorIndex[vectorID])

    def centroid(self, listOfIDs):
        c = zeros( (self.numberOfTerms) )
        for docId in listOfIDs:
            c = add(c, self.vectorIndex[docId])
        c = c / len(listOfIDs)
        return c

    def randomSeed(self, k):
        w = []
        # Initialize random class lists
        for i in range(k):
            w.append([])
        for docId in self.indexer.docL.keys():
            w[random.randrange(0,k)].append(docId)
        return w

    def calculateClassRSS(self, v, c):
        """v: list of docIds in the class; c: centroid for the class"""
        rss = 0.0
        for docId in v:
            rss += sum( (c - self.vectorIndex[docId])**2.0 )
        return rss

    def calculateRSS(self, w, u):
        """w: list of classes; u: list of centroids"""
        result = 0.0
        for k in range(len(w)):
            result += self.calculateClassRSS(w[k], u[k])
        return result

    def kMeans(self, k):
        # Initial seed and centroid
        w = self.randomSeed(k)
        u = []
        for i in range(k):
            u.append(self.centroid(w[i]))
        thisRSS = self.calculateRSS(w, u)
        prevRSS = 0
        while thisRSS != prevRSS:
            # Set each doc to the class with the nearest centroid
            for i in range(k):
                w[i] = []
            for docId in self.indexer.docL.keys():
                # distances from current docId to all centroids
                distances = [ distance(u[i], self.vectorIndex[docId]) for i in range(k) ]
                j = min(xrange(k), key=distances.__getitem__)
                w[j].append(docId)
            # Calculate the new centroids and RSS
            for i in range(k):
                u[i] = self.centroid(w[i])
            prevRSS = thisRSS
            thisRSS = self.calculateRSS(w, u)
        return w, u, thisRSS

    def kMeansBestOfN(self, k, n):
        rss = 0
        w = u = []
        for i in range(n):
            thisW, thisU, thisRSS = self.kMeans(k)
            if thisRSS < rss or rss == 0:
                rss = thisRSS
                w = thisW
                u = thisU
        return w, u, rss

    def nearestCluster(self, w, u, vector):
        distances = [ distance(u[i], vector) for i in range(len(u)) ]
        j = min(xrange(len(u)), key=distances.__getitem__)
        return w[j]
        
"""
def kMeansPlot()
    results = []
    tries = []
    for i in range(2, 100)
        kMeans(i)
"""
def main():
    index = ii.InvertedIndex()
    indexer = wi.WebIndexer()
    ii.load("../index/fullindex.csv", index)
    vectorSpace = VectorSpace(index, indexer)
    vectorSpace.buildVectors()

    # Length tests
    length(vectorIndex, 1)
    length(vectorIndex, 2)
    length(index, 3)
    length(index, 4)

    # Centroid test
    centroid = findCentroid( index, [1,2,3], numberOfTerms )
    vectorLength(centroid)

    # Dot product
    print vdot(index[100], index[5])

    # Distance
    a1 = array ( [1,2,3,4,5,6,7,8] )
    a2 = array ( [ 0,1,2,3,4,5,6,7] )
    print distance(index, 1, 2)

#main()
