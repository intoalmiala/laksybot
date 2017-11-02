import json
luokka = input("Minkä luokan lukujärjestystä haluat katsella: ").upper()
päivä = input("Minkä päivän lukujärjestystä haluat tarkastella: ").lower()
array = ["8.15-9.30","9.45-11.00","11.45-13.00","13.15-14.30","14.45-16.00"]
dictionary = {}
with open("json.json","r") as filu:
	dictionary = json.load(filu)
if luokka in dictionary:
	if päivä in dictionary[luokka]:
		for i in sorted(dictionary[luokka][päivä],key=array.index):
			print(i,dictionary[luokka][päivä][i])
