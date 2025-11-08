# def display_name(arr):
#     sum = 0
#     for i in arr :
#         sum=sum+i
#     print (len(arr),sum)
#     return sum/len(arr);

# avg=display_name([1,2,3,50,6,9,4,233,232,44])
# print(avg)


# def display_name2(firstname, lastname ,middlename):
#     print(firstname,middlename,lastname)

# display_name2(lastname='chandrashekar',middlename='kumar',firstname='vijay')

def STRINGCONCATENATION(word,delimiter):
    finalword=""
    for i in range(0,len(word)):
        if(i==len(word)-1):       
          finalword=finalword+word[i]
        else:
             finalword=finalword+word[i]+delimiter
    return finalword
print(STRINGCONCATENATION(['asasas',"sdsfdfsdf",'dfgdfdfdfdfdfd','hghghghghg'],'@'))

### 1st iteration 
### i=asasas finalword=""  -> asasas@
### i=sdsf  finalword=asasas@ ->asasas@sdsfdfsdf#

