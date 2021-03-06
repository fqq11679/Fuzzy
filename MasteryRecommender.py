#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Ver_0213

from math import exp, log, fabs, sqrt
from random import *
from JRecRequest import JRecRequest

class MasteryRecommender:

    INIT_MASTERY = 2.0
    MAX_MASTERY = 4.0       # Mastered
    MIN_MASTERY = 0.0       # Not Mastered
    YES_MASTERY = 3.0
    NO_MASTERY  = 1.0

    STOP_LEARN = 18

    ML_RATE = 0.8
    DEFAULT_TRADEOFF = 0.6
    NEW_WORD_PENALTY = 0.8

    def __init__(self, articles):

        # mastery = -log(P_understand)

        self.articles = articles

        self.content = []
        with open("C:\\Users\\fqq11\\Downloads\\JNLP\\JRec\\Dict.txt") as f:
            self.content = f.readlines()
        self.content = [x.strip() for x in self.content]

        self.mastery = {}
        self.default_mastery = MasteryRecommender.INIT_MASTERY
        self.decided_words = 0
        self.random = Random()
        self.request_history = []
        self.response_history = []
        self.recommend_mastery = MasteryRecommender.INIT_MASTERY
        self.recommend_mastery_upperbound = MasteryRecommender.MAX_MASTERY
        self.recommend_mastery_lowerbound = MasteryRecommender.MIN_MASTERY


    def word_mastery(self,w):
        if self.mastery.has_key(w):
            return self.mastery[w] #+ 0.3*self.NEW_WORD_PENALTY
        else:
            #return 2.0

            #return self.default_mastery
            freqw = self.content.index(w.encode('utf8')) if w.encode('utf8') in self.content else 10000.0
            return self.default_mastery + (10000.0 - freqw )/30000.0

    def article_mastery(self, article):
#        for w in article.uniq_wordlist:
#            if self.mastery.has_key(w):
#                pass
#                #self.mastery[w] = min(self.mastery[w], Recommender.MIN_MASTERY)
#            else:
#                self.mastery[w] = self.average_mastery
        #return float(sum([self.mastery[w] for w in article.uniq_wordlist])) / sqrt(len(article.uniq_wordlist))
        return float(sum([self.word_mastery(w) for w in article.uniq_wordlist])) / len(article.uniq_wordlist)

    def request(self):
        if len(self.response_history) < len(self.request_history):
            return JRecRequest(self.articles[self.request_history[-1]])
        res = [[id,self.article_mastery(self.articles[id])] for id in self.articles.keys() if not id in self.request_history]
        if len(res) == 0:
            return None
        self.random.shuffle(res)
        res.sort(key=lambda x:fabs(self.recommend_mastery - x[1]))
        #print self.recommend_mastery, res[0][1], [t[1] for t in res]
        self.request_history.append(res[0][0])
        return JRecRequest(self.articles[self.request_history[-1]])

    def response(self, res):
        article = self.articles[self.request_history[-1]]
        self.response_history.append(res)


        print "-------------------------------------------------"
        for w in article.uniq_wordlist:
            print w + "-"
            print self.content.index(w.encode('utf8')) if w.encode('utf8') in self.content else 10000
            freqw = self.content.index(w.encode('utf8')) if w.encode('utf8') in self.content else 10000.0
            print (10000.0 - freqw) / 10000.0

        expected_response = self.article_mastery(article) # / len(article.uniq_wordlist)
        if res.understood == True:
            actual_response = MasteryRecommender.YES_MASTERY
            recommend_mastery_offset = -1
        elif res.understood == False:
            actual_response = MasteryRecommender.NO_MASTERY
            recommend_mastery_offset = 1
        else:
            actual_response = res.understood
            if actual_response > 2:
                recommend_mastery_offset = -1
            else:
                recommend_mastery_offset = 1
        step = (actual_response - expected_response) * self.ML_RATE
        step = step / len(article.uniq_wordlist)
        num_change = len([w for w in article.uniq_wordlist
                          if not self.mastery.has_key(w) or
                          self.mastery[w] > MasteryRecommender.MIN_MASTERY and
                          self.mastery[w] < MasteryRecommender.MAX_MASTERY])

        if num_change > 0:
            step = step * len(article.uniq_wordlist) / num_change

        zzz = 0.0

        if len(self.response_history) <= self.STOP_LEARN:
            for w in article.uniq_wordlist:
                if not self.mastery.has_key(w):
                    zzz = zzz+1.0
                    self.mastery[w] = self.default_mastery + step # + self.NEW_WORD_PENALTY
                elif self.mastery[w] > MasteryRecommender.MIN_MASTERY and self.mastery[w] < MasteryRecommender.MAX_MASTERY:
                    self.mastery[w] += step
                if self.mastery[w] > MasteryRecommender.MAX_MASTERY:
                    self.mastery[w] = MasteryRecommender.MAX_MASTERY
                if self.mastery[w] < MasteryRecommender.MIN_MASTERY:
                    self.mastery[w] = MasteryRecommender.MIN_MASTERY

        zzz = zzz/len(article.uniq_wordlist)
        print zzz
        if zzz > 0.5:
            if res.understood == True:
                self.NEW_WORD_PENALTY = self.NEW_WORD_PENALTY * 1;

#        if zzz < 0.5:
#            if res.understood == False:
#               self.NEW_WORD_PENALTY = self.NEW_WORD_PENALTY * 1.2;

        #if len(self.response_history) < 3:
        #    self.recommend_mastery += recommend_mastery_offset * 0.3
        #elif len(self.response_history) < 10:
        #    self.recommend_mastery += recommend_mastery_offset * 0.1
        #else:
        #    self.recommend_mastery += recommend_mastery_offset * 0.05

        #if len(self.response_history) <= 8:
        #    self.recommend_mastery += recommend_mastery_offset * 0.3
        #else:
        #    if recommend_mastery_offset > 0:
        #        self.recommend_mastery_lowerbound = \
        #            (self.recommend_mastery_lowerbound + self.recommend_mastery_upperbound) / 2
        #    else:
        #        self.recommend_mastery_upperbound = \
        #            (self.recommend_mastery_lowerbound + self.recommend_mastery_upperbound) / 2
        #    self.recommend_mastery = (self.recommend_mastery_lowerbound + self.recommend_mastery_upperbound) / 2

        if len(self.response_history) < 5:
            self.recommend_mastery += recommend_mastery_offset * 0.3
        elif len(self.response_history) <= self.STOP_LEARN:
            self.recommend_mastery += recommend_mastery_offset * 0.1
        else:
            if recommend_mastery_offset > 0:
                self.recommend_mastery_lowerbound = \
                    (self.recommend_mastery_lowerbound + self.recommend_mastery_upperbound) / 2
            else:
                self.recommend_mastery_upperbound = \
                    (self.recommend_mastery_lowerbound + self.recommend_mastery_upperbound) / 2
            self.recommend_mastery = (self.recommend_mastery_lowerbound + self.recommend_mastery_upperbound) / 2



        if self.recommend_mastery > MasteryRecommender.MAX_MASTERY:
            self.recommend_mastery = MasteryRecommender.MAX_MASTERY
        if self.recommend_mastery < MasteryRecommender.MIN_MASTERY:
            self.recommend_mastery = MasteryRecommender.MIN_MASTERY

        #self.default_mastery = self.default_mastery - self.NEW_WORD_PENALTY
        self.default_mastery = sum(self.mastery.values()) / len(self.mastery.values()) * self.DEFAULT_TRADEOFF + \
                                self.INIT_MASTERY * (1 - self.DEFAULT_TRADEOFF) - self.NEW_WORD_PENALTY
  #      if self.default_mastery > MasteryRecommender.MAX_MASTERY:
 #           self.default_mastery = MasteryRecommender.MAX_MASTERY
 #       if self.default_mastery < MasteryRecommender.MIN_MASTERY:
 #           self.default_mastery = MasteryRecommender.MIN_MASTERY

        self.decided_words = len([i for i in self.mastery.values() if i == MasteryRecommender.MIN_MASTERY or i == MasteryRecommender.MAX_MASTERY])
