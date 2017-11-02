import random,datetime,json,string,uuid


print("hei, sinulta kysytään viikonpäivän tunnit, kirjoita siihen että mikä tunti sinulla on, jos sinulla ei ole tuntia niin vastaa '-'")
viikonpäivät = ["maanantai","tiistai","keskiviikko","torstai","perjantai"]
tunnit = ["8.15-9.30","9.45-11.00","11.45-13.00","13.15-14.30","14.45-16.00"]
with open("json.json","r") as filu:
	dictionary = json.load(filu)
print("\n")
luokka = input("luokka/koulu (esim. 8c/olari): ").upper()
print(luokka)
if luokka not in dictionary:
    dictionary[luokka] = {}
    for i in viikonpäivät:
        dictionary[luokka][i] = {}
        for j in tunnit:
            dictionary[luokka][i][j] = input("{},{}: ".format(i,j))
    dictionary[luokka]["password"] = str(uuid.uuid4())[:7]
    print("muokkaamiskoodisi on {}, jaa tämä ryhmääsi jos haluat joskus muokata lukujärjestystä".format(dictionary[luokka]["password"]))
    with open("json.json","w") as filu:
        json.dump(dictionary,filu)
else:
    vastaus = input("Luokka on jo olemassa, haluatko muokata lukujärjestystä, vastaa 'kyllä' tai 'ei': ")
    if(vastaus=="kyllä"):
        koodi = input("Syötä muokkaamiskoodi: ")
    if koodi == dictionary[luokka]["password"]:
        päivät = input("Mitä päiviä haluat muokata (jos haluat kaiken, kirjoita 'kaikki': ")
        if päivät == "kaikki":
            for i in viikonpäivät:
                dictionary[luokka][i] = {}
                for j in tunnit:
                    dictionary[luokka][i][j] = input("{},{}: ".format(i,j))
        elif päivät in viikonpäivät:
            hetket = input("Minkä tunnin haluat uusia, kirjoita vastaus muotoa 8.15-9.30 (jos haluat kaiken kirjoita 'kaikki': ")
            if hetket == "kaikki":
                for i in tunnit:
                    dictionary[luokka][päivät][i] = input("{},{}: ".format(päivät,i))
            elif hetket in tunnit:
                dictionary[luokka][päivät][hetket] = input("{},{}: ".format(päivät,hetket))
            else:
                print("Ei ollut validi aika")
        else:
            print("ei ollut validi aika")
        with open("json.json","w") as filu:
            json.dump(dictionary,filu)



