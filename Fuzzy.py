# This Python file uses the following encoding: utf-8
# encoding: utf-8

from Article import Article
import nhk_easy
import collections

sentences = []

articles = nhk_easy.read_articles()
for key in articles:
    if key.find("_s") != -1:
        #print key
        sentences.append(articles[key])

def num_common_concepts(s1, s2):
    return len(list((collections.Counter(s1.wordlist) & collections.Counter(s2.wordlist)).elements()))

#print len(sentences)
sentences = sentences[0:260];#
num_sentences = len(sentences);

G = [[0 for x in range(num_sentences)] for y in range(num_sentences)]
E = [[0 for x in range(num_sentences)] for y in range(num_sentences)]

num_edges = 0

for i in range(num_sentences):
    for j in range(num_sentences):
        G[i][j] =  float(num_common_concepts(sentences[i], sentences[j]))/float(len(sentences[i].wordlist))
        if(G[i][j] < 0.5):
            G[i][j] = 0.0;
        else:
            num_edges = num_edges+1;

print "the matrix is ready"

print num_edges

for i in range(num_sentences):
    for j in range(num_sentences):
        E[i][j] = G[i][j];

for k in range(num_sentences):
    for i in range(num_sentences):
        for j in range(num_sentences):
            if G[i][k] * G[k][j] > G[i][j]:
                G[i][j] = G[i][k] * G[k][j];

count = 0
for i in range(num_sentences):
    for j in range(num_sentences):
        for k in range(num_sentences):
            if E[i][j] == 0:
                break;
            if k != i and k != j:
                if G[i][k] * G[k][j] >= E[i][j]:
                    E[i][j] = 0;
                    count = count+1;

#print count

#edge_count = 0
#for i in range(num_sentences):
#    for j in range(num_sentences):
#        if E[i][j] != 0:
#            edge_count = edge_count + 1;
#print edge_count
#print articles

P_Understand = [0.0 for x in range(num_sentences)];
P_Dont_Understand = [0.0 for x in range(num_sentences)];

def update(x, res):
    if res == 1:
        for i in range(num_sentences):
            if G[i][x] > P_Understand[i]:
                P_Understand[i] = G[i][x];
    if res == 0:
        for i in range(num_sentences):
            if G[x][i] > P_Dont_Understand[i]:
                P_Dont_Understand[i] = G[x][i];
    return;

#for i in range(num_sentences/2):
for i in range(20):
    update(i, 1)


def get_color(v, threshold):
    if P_Understand[v] > P_Dont_Understand[v]:
        if P_Understand[v] > threshold:
            return 1;
        else:
            return 0;
    else:
        if 1.0-P_Dont_Understand[v]>threshold:
            return 1;
        else:
            return 0;

num_error = 0;
border = 20
#border = 20
for i in range(num_sentences):
    if i <= border:
        if get_color(i, 0.6) != 1:
            num_error = num_error + 1;
    if i > border:
        if get_color(i, 0.6) != 0:
            num_error = num_error + 1;

print num_error
print P_Understand
print P_Dont_Understand


C = [[0 for x in range(num_sentences)] for y in range(num_sentences)]
for i in range(num_sentences):
    for j in range(num_sentences):
        if i==j:
            continue;
        if E[i][j] == 0:
            C[i][j] = 9999;
        else:
            C[i][j] = 1;

for k in range(num_sentences):
    for i in range(num_sentences):
        for j in range(num_sentences):
            if C[i][k] + C[k][j] > C[i][j] and G[i][k]*G[k][j]>0.05:
                C[i][j] = C[i][k] + C[k][j];

def get_dist(v, threshold):
    ans = 9999;
    for i in range(num_sentences):
        if get_color(v, threshold) != get_color(i, threshold):
            if C[v][i] < ans:
                if G[v][i] > 0.0:
                    ans = C[v][i];
    return ans;

for i in range(num_sentences):
    if get_color(i, 0.6) == 0:
        if get_dist(i, 0.6) != 9999:
           print get_dist(i, 0.6)

#
boundary = []
def add_to_boundary(v):
    for i in range(num_sentences):
        if i != v:
            if E[v][i] > 0:
                if E[v][i] >= E[i][v]:
                    return;
    boundary.append(v);
    return;

for i in range(num_sentences):
    if get_color(i, 0.6) == 1:
        add_to_boundary(i)

print boundary;

def dist_to_boundary(v):
    ans = 9999
    for x in boundary:
        if x != v:
            if C[v][x] < ans:
                ans = C[v][x];
    return ans;



for i in range(num_sentences):
    if get_color(i, 0.6) == 1:
        if dist_to_boundary(i) != 9999:
            print dist_to_boundary(i)
