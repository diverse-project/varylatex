from famapy.core.discover import DiscoverMetamodels # This loads the tool in the python execution eviroment
import random

def transcodeProducts(rawProducts):
    transcoddedRes=[]
    for result in rawProducts:
        r={}
        if "PL_FOOTNOTE" in result:
            r["PL_FOOTNOTE"]=True
        else:
            r["PL_FOOTNOTE"]=False
        
        if "ACK" in result:
            r["ACK"]=True
        else:
            r["ACK"]=False
        
        if "LONG_AFFILIATION" in result:
            r["LONG_AFFILIATION"]=True
        else:
            r["LONG_AFFILIATION"]=False
        
        if "EMAIL" in result:
            r["EMAIL"]=True
        else:
            r["EMAIL"]=False
        
        if "LONG_ACK" in result:
            r["LONG_ACK"]=True
        else:
            r["LONG_ACK"]=False
        
        if "vspace_ONE" in result:
            r["vspace"]=1
        elif "vspace_FIVE" in result:
            r["vspace"]=5
        elif "vspace_TWO" in result:
            r["vspace"]=2
        else:
            raise Exception
        
        if "bref_size_POINT_SEVEN" in result:
            r["bref_size"]=0.7
        elif "bref_size_ONE" in result:
            r["bref_size"]=1
        elif "bref_size_TWO" in result:
            r["bref_size"]=2
        else:
            raise Exception
        
        if "cserver_size_POINT_SIX" in result:
            r["cserver_size"]=0.6
        elif "cserver_size_POINT_NINE" in result:
            r["cserver_size"]=0.9
        elif "cserver_size_TWO" in result:
            r["cserver_size"]=2
        else:
            raise Exception
        
        if "tiny" in result:
            r["js_style"]="\\tiny"
        elif "scriptsize" in result:
            r["js_style"]="\\scriptsize"
        elif "footnotesize" in result:
            r["js_style"]="\\footnotesize"

        if "PARAGRAPH_ACK" in result:
            r["PARAGRAPH_ACK"]=True
        else:
            r["PARAGRAPH_ACK"]=False

        if "BOLD_ACK" in result:
            r["BOLD_ACK"]=True
        else:
            r["BOLD_ACK"]=False

        transcoddedRes.append(r)
    return transcoddedRes

def getProducts(path):
    dm = DiscoverMetamodels()
    results = dm.use_operation_from_file("Products", path) # This launch the operation and stores the result on the result variable
    results = transcodeProducts(results)
    return results


def getRandomProduct(products):
    n = random.randint(0,len(products)-1)
    return products[n]

def getFeatureHeaders(path):
    #This is still hardcoded for the example. TODO See how to generalize
    return ["PL_FOOTNOTE", "ACK", "LONG_AFFILIATION", "EMAIL", "LONG_ACK", "vspace_bib", "bref_size", "cserver_size", "js_style", "PARAGRAPH_ACK", "BOLD_ACK", "nbPages", "space"]
