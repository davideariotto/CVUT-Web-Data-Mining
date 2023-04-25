# Reading csv to a data frame
import pandas as pd

sem = pd.read_csv('./wum_dataset_hw/search_engine_map.csv')

visitors = pd.read_csv('./wum_dataset_hw/visitors.csv')

clicks = pd.read_csv('./wum_dataset_hw/clicks.csv')


# select column
#print(df[['age', 'car']])

# select by index
#print(df.iloc[3:6, 5:9])

# delete column
#del df["id"]
#print(df.head())

#print(df.head())

from collections import Counter


def frequentItems(transactions, support):
    counter = Counter()
    for trans in transactions:
        counter.update(frozenset([t]) for t in trans)
    return set(item for item in counter if counter[item] / len(transactions) >= support), counter


def generateCandidates(L, k):
    candidates = set()
    for a in L:
        for b in L:
            union = a | b
            if len(union) == k and a != b:
                candidates.add(union)
    return candidates


def filterCandidates(transactions, itemsets, support):
    counter = Counter()
    for trans in transactions:
        subsets = [itemset for itemset in itemsets if itemset.issubset(trans)]
        counter.update(subsets)
    return set(item for item in counter if counter[item] / len(transactions) >= support), counter


def apriori(transactions, support):
    result = list()
    resultc = Counter()
    candidates, counter = frequentItems(transactions, support)
    result += candidates
    resultc += counter
    k = 2
    while candidates:
        candidates = generateCandidates(candidates, k)
        candidates, counter = filterCandidates(transactions, candidates, support)
        result += candidates
        resultc += counter
        k += 1
    resultc = {item: (resultc[item] / len(transactions)) for item in resultc}
    return result, resultc


def genereateRules(frequentItemsets, supports, minConfidence):
    print("{--------------------------------------------------------}")

    print("                generate rules min Confidence {}".format(minConfidence))
    print("{--------------------------------------------------------}")

    results = []

    for item in frequentItemsets:
        #subset of 1 is 1
        if len(item) < 2:
            continue
#create subsets
        tmp = list(item)
        subsets = []
        for i in tmp:
            tmplist=list(tmp)
            tmplist.remove(i)
            subsets.append((tmplist, i))

        for subset in subsets:
            conf = supports[item] / supports[frozenset(subset[0])]
            if conf >= minConfidence:
                results.append((subset[0], subset[1], conf, supports[item]))
    results = sorted(results, key=lambda rule: rule[2], reverse=True)

    for res in results[:100]:
        set1 = res[0]
        set2=res[1]
        conf=res[2]
        supp = res[3]
        print("{} => {} has conf: {} and supp {} ".format(set1,set2,conf,supp))
    return results



print("visits \n {} \n".format(visitors["VisitID"].count()))

print("users \n {} \n".format(sem["Referrer"].count()))

print("clicks \n {} \n".format(clicks["LocalID"].count()))

print("stredni doba TimeOnPage \n {} \n".format(clicks["TimeOnPage"].mean()))

print("stredni doba TimeOnPage \n {} \n".format(clicks["TimeOnPage"].mean()))



df=pd.merge(clicks, visitors, how='left', on='VisitID')

df=pd.merge(df, sem, how='left', on='Referrer')



# remove too short visits

df = df[df.Length_seconds > 2]

# page score has to be splitted

df["PageScore"] = pd.cut(df["PageScore"],5)

# others
df["TimeOnPage"] = pd.cut(df["TimeOnPage"],5)

df["Length_seconds"] = pd.cut(df["Length_seconds"],10)
df["Hour"] = pd.cut(df["Hour"],4)


#df["Length_pagecount"] = pd.cut(df["Length_pagecount"],20)

del df["LocalID"]
del df["CatID"]
del df["ExtCatID"]
del df["TopicID"]

#new_df = pd.merge(A_df, B_df,  how='left', left_on=['A_c1','c2'], right_on = ['B_c1','c2'])


print("head \n")  # df.tail()
print(df.head())  # df.tail()

#print(df)



dataset = []
for index, row in df.iterrows():
    row = [col + "=" + str(row[col]) for col in list(df)]
    dataset.append(row)

frequentItemsets, supports = apriori(dataset, 0.05)

for f in frequentItemsets:
    print("{} - {}".format(f, supports[f]))

genereateRules(frequentItemsets, supports, 0.4)

# ...
# {'car=YES'} => married=YES, 0.3233333333333333, 0.6554054054054054
# ...
# {'married=YES', 'save_act=YES'} => current_act=YES, 0.3433333333333333, 0.7436823104693141
# ...