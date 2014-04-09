import sys


def run(fname):
    '''
    :param args: Python output file of the Clafer compiler. Generated with argument "-m python".
    :type args: file
    
    Starting point for ClaferZ3.
    '''
    with open(fname) as f:
        content = f.readlines()
    content = [i.rstrip().replace("$","__") for i in content]
    #content = [i.rstrip() for i in content]
        
    currFeature = ""
    currCard = ""
    currGCard = ""
    
    currCon = ""
    currConLeft = ""
    currConRight = ""
    currConOp = ""

    mostRecentFeature = ""
    currParent = ""

    features = []
    constraints = []
    parentConstraints = []
    
    while content:
        i = content.pop(0)
        if i.startswith("Feature"):
            currFeature = i
        elif "type" in i:
            if "Optional" in i:
                currCard = " ?"
            else:
                currCard = " "
        elif "gcard" in i:
            if "Xor" in i:
                currGCard = "xor" #"1..1"
            elif "Some" in i:
                currGCard = "some" #"1..*"
            else:
                currGCard = "" #"0..*"
        elif "conType" in i:
            if "Include" in i:
                currConPrefix = ""
                currConOp = " => "
                currConSuffix = ""
            else:
                currConPrefix = "!("
                currConOp = " && "
                currConSuffix = ")"
        elif "parent_feature" in i:
            s = i.split(" = ")
            currParent = s[1]
        elif "left" in i:
            s = i.split(" = ")
            currConLeft = s[1]
        elif "right" in i:
            s = i.split(" = ")
            currConRight = s[1]
        
        if(currConLeft != "" and currConRight != "" and currConOp != ""):
            constraints.append("[" + currConPrefix + currConLeft + currConOp + currConRight + currConSuffix + "]")
            currConLeft = ""
            currConRight = ""
            currConOp = ""
        
        if(currCard != "" and currGCard != "" and currFeature != ""):
            constraints.append(currGCard + " " + currFeature + currCard)
            mostRecentFeature = currFeature
            currFeature = ""
            currCard = ""
            currGCard = ""
        if currParent != "":
            parentConstraints.append("[" + mostRecentFeature + " => " + currParent + "]") 
            currParent = ""
            
    print("// Features")
    for i in features:
        print(i)
    print("\n// Constraints")
    for i in constraints:
        print(i) 
    print("\n// Parent Constraints")
    for i in parentConstraints:
        print(i)
   
if __name__ == '__main__':
    run(sys.argv[1])
