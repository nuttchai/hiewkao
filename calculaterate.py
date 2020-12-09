def calRate(rateDetail, userRate):

    # format => {"rate": [], "avgRate":""}
    allRate = rateDetail["rate"]
    avgRate = rateDetail["avgRate"]

    if avgRate == "": 
        allRate.append(userRate)
        avgRate = userRate
    
    else:
        allRate.append(userRate)
        avgRate = round((float(avgRate) * (len(allRate) - 1) + float(userRate)) / len(allRate), 1)
    
    rateDetail["rate"] = allRate
    rateDetail["avgRate"]  = avgRate

    return rateDetail

