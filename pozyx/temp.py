

if __name__ == "__main__":
      


    rangingAge = {11: 21, 4: 23, 13: 10, 6: 50}
    
    sortRangingAge = sorted(rangingAge.items(), key=lambda x: x[1],reverse=True)
    #sortRangingAge = {k: v for k, v in sorted(rangingAge.items(), key=lambda item: item[1])}
    print(rangingAge, " sorted ", sortRangingAge)
