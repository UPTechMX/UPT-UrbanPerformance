#This function recive an array of model objects and a id and return the index of id gived or -1 if it's not in the array
def getIdIndex(objects_list, id):
    tam = len(objects_list)
    i=0
    band=True
    while band:
        if objects_list[i].id == id:
            return i
        elif tam == i+1:
            return -1
        else:
            i+=1