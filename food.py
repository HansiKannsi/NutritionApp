from enum import Enum
from datetime import date

class FoodType(Enum):
    MEAT = 1
    FISH = 2
    DAIRY = 3
    VEGGIE = 4
    CARB = 5
    FAT = 6
    EGG = 7
    
class NutritionValues:
    def __init__(self, P, K, F, C, B, reference = 100):
        self.P = P
        self.K = K
        self.F = F
        self.C = C
        self.B = B
        self.reference = reference
        
    def addNutritionValues(self, amount, total):
        factor = amount / self.reference
        total.P = total.P + self.P * factor
        total.K = total.K + self.K * factor
        total.F = total.F + self.F * factor
        total.C = total.C + self.C * factor
        total.B = total.B + self.B * factor
        
        return total
    
    def print(self, output):
        #"{:.1f}".format(number)
        output += "\t\tKal.: {:.1f} kcal\n".format(self.C)
        output += "\t\tProt: {:.1f} g\n".format(self.P)
        output += "\t\tCarb: {:.1f} g\n".format(self.K)
        output += "\t\tFett: {:.1f} g\n".format(self.F)
        output += "\t\tBall: {:.1f} g\n\n".format(self.B)
        
        return output

class FoodItemsDatabase:
    def __init__(self):
        self.foodItems = []
        self.foodItems.append(FoodItem("Haehnchenbrust", FoodType.MEAT, NutritionValues(22.0, 0.0, 2.0, 109, 0.0)))
        
        self.foodItems.append(FoodItem("Kabeljau", FoodType.FISH, NutritionValues(19.0, 0.5, 0.7, 80, 0.0)))
        self.foodItems.append(FoodItem("Thunfisch", FoodType.FISH, NutritionValues(28.0, 0.0, 0.8, 120, 0.0)))
        self.foodItems.append(FoodItem("Lachs", FoodType.FISH, NutritionValues(19.0, 0.0, 13.5, 198, 0.0)))
        self.foodItems.append(FoodItem("Wildlachs", FoodType.FISH, NutritionValues(21.0, 0.5, 1.8, 101, 0.0)))        
        
        self.foodItems.append(FoodItem("Proteinmilch", FoodType.DAIRY, NutritionValues(7.5, 4.8, 0.9, 58, 0.0)))
        self.foodItems.append(FoodItem("Quark", FoodType.DAIRY, NutritionValues(12.0, 4.1, 0.2, 68, 0.0)))
        self.foodItems.append(FoodItem("ProteinESN", FoodType.DAIRY, NutritionValues(82.0, 3.0, 4.7, 362, 0.0)))
        self.foodItems.append(FoodItem("ProteinRuhl", FoodType.DAIRY, NutritionValues(90.0, 0.5, 0.3, 376, 0.0)))
        self.foodItems.append(FoodItem("EiProtein", FoodType.EGG, NutritionValues(94.0, 0.0, 0.0, 400, 0.0)))        
        self.foodItems.append(FoodItem("Skyr", FoodType.DAIRY, NutritionValues(11.0, 4.0, 0.2, 68, 0.0)))
        self.foodItems.append(FoodItem("Exquisa", FoodType.DAIRY, NutritionValues(12.5, 4.4, 0.3, 70, 0.0)))
        
        self.foodItems.append(FoodItem("Haferflocken", FoodType.CARB, NutritionValues(13.5, 58.7, 7.0, 372, 10.0)))
        self.foodItems.append(FoodItem("Dinkelmehl", FoodType.CARB, NutritionValues(14.0, 64.0, 2.6, 372, 8.4)))
        self.foodItems.append(FoodItem("Weizenmehl", FoodType.CARB, NutritionValues(11.0, 60.0, 1.8, 327, 13.0)))
        self.foodItems.append(FoodItem("Reis", FoodType.CARB, NutritionValues(7.9, 76.0, 1.0, 372, 3.0)))
        
        self.foodItems.append(FoodItem("Apfel", FoodType.VEGGIE, NutritionValues(0.0, 14.0, 0.0, 52, 2.4)))
        self.foodItems.append(FoodItem("Kaisergemuese", FoodType.VEGGIE, NutritionValues(1.6, 4.0, 0.5, 28, 1.2)))
        self.foodItems.append(FoodItem("Brokkoli", FoodType.VEGGIE, NutritionValues(2.7, 1.8, 0.3, 26, 2.6)))
        self.foodItems.append(FoodItem("Karotten", FoodType.VEGGIE, NutritionValues(0.9, 4.8, 0.2, 25, 3.6)))
        self.foodItems.append(FoodItem("Bananen", FoodType.VEGGIE, NutritionValues(1.0, 22.8, 0.2, 89, 2.6)))
        self.foodItems.append(FoodItem("Heidelbeeren", FoodType.VEGGIE, NutritionValues(0.6, 11.3, 0.4, 58, 4.9)))
        self.foodItems.append(FoodItem("Zucchini", FoodType.VEGGIE, NutritionValues(1.2, 3.1, 0.3, 33, 1.0)))
        self.foodItems.append(FoodItem("Paprika", FoodType.VEGGIE, NutritionValues(1.3, 6.4, 0.5, 43, 3.6)))
        self.foodItems.append(FoodItem("Passata", FoodType.VEGGIE, NutritionValues(1.4, 3.6, 0.2, 24, 1.0)))
        
        self.foodItems.append(FoodItem("Mandeln", FoodType.FAT, NutritionValues(24.0, 5.7, 53.0, 619, 11.0)))
        self.foodItems.append(FoodItem("NuesseAction", FoodType.FAT, NutritionValues(19.1, 10.0, 57.7, 648, 6.7)))
        self.foodItems.append(FoodItem("NuesseRM", FoodType.FAT, NutritionValues(22.0, 12.0, 53.0, 632, 6.7)))
        self.foodItems.append(FoodItem("Walnuesse", FoodType.FAT, NutritionValues(15.9, 7.4, 65.1, 691, 5.7)))
        self.foodItems.append(FoodItem("Leinsamen", FoodType.FAT, NutritionValues(21.2, 1.6, 40.6, 514, 28.5)))
        self.foodItems.append(FoodItem("Chiasamen", FoodType.FAT, NutritionValues(21.0, 1.5, 31.0, 443, 31.0)))        
        self.foodItems.append(FoodItem("Erdnussmus", FoodType.FAT, NutritionValues(28.0, 7.1, 52, 630, 11.0)))
        self.foodItems.append(FoodItem("Mandelmus", FoodType.FAT, NutritionValues(25.0, 5.4, 56, 653, 12.0)))
        self.foodItems.append(FoodItem("Ei", FoodType.EGG, NutritionValues(13.0, 1.1, 11.0, 155, 0.0)))
        self.foodItems.append(FoodItem("Kidneybohnen", FoodType.CARB, NutritionValues(7.2, 11.0, 0.5, 95, 0.0)))
        self.foodItems.append(FoodItem("Aldibrot", FoodType.CARB, NutritionValues(4.2, 34.0, 1.2, 184, 9.0)))
        self.foodItems.append(FoodItem("Steinofenbrot", FoodType.CARB, NutritionValues(8.4, 38.3, 3.7, 222, 9.0)))  
        self.foodItems.append(FoodItem("Saatenbrot", FoodType.CARB, NutritionValues(6.6, 30.6, 9.5, 255, 10.2)))                 
        self.foodItems.append(FoodItem("Reiswaffeln", FoodType.CARB, NutritionValues(8.2, 80.0, 1.9, 376, 2.2)))
        self.foodItems.append(FoodItem("Maiswaffeln", FoodType.CARB, NutritionValues(7.0, 85.0, 1.4, 384, 1.7))) 
        self.foodItems.append(FoodItem("Dinkelwaffeln", FoodType.CARB, NutritionValues(12.0, 75.0, 2.2, 381, 6.6)))       
        self.foodItems.append(FoodItem("Kartoffeln", FoodType.CARB, NutritionValues(2.0, 15.0, 0.2, 73, 1.2)))
        self.foodItems.append(FoodItem("Spaghetti", FoodType.CARB, NutritionValues(12.0, 66.0, 2.5, 350, 4.7)))
        self.foodItems.append(FoodItem("Dattelriegel", FoodType.CARB, NutritionValues(14.0, 40.0, 25.0, 453, 6.0)))
        self.foodItems.append(FoodItem("GKBratlinge", FoodType.CARB, NutritionValues(13.0, 55.0, 7.9, 363, 9.9)))
        self.foodItems.append(FoodItem("Dinkellocken", FoodType.CARB, NutritionValues(13.0, 62.0, 2.4, 344, 11.0)))        
        
        self.foodItems.append(FoodItem("Sonnenblumenoel", FoodType.FAT, NutritionValues(0.0, 0.0, 100, 880, 0.0)))
        self.foodItems.append(FoodItem("Olivenoel", FoodType.FAT, NutritionValues(0.0, 0.0, 92.0, 828, 0.0)))
        self.foodItems.append(FoodItem("Senf", FoodType.FAT, NutritionValues(7.3, 1.4, 10.0, 133, 0.0)))
        self.foodItems.append(FoodItem("Pesto", FoodType.FAT, NutritionValues(1.5, 5.2, 26.0, 267, 1.2)))
        self.foodItems.append(FoodItem("Avocado", FoodType.FAT, NutritionValues(2.0, 9.0, 15.0, 160, 7.0)))        
        
    def getByName(self, name):
        return next((x for x in self.foodItems if x.name == name), None)
    
class FoodItem:
    def __init__(self, name, foodtype, nutritionValue):
        self.name = name
        self.type = foodtype
        self.nutritionValue = nutritionValue
        
class MealItem:
    def __init__(self, foodItem, amount):
        self.foodItem = foodItem
        self.amount = amount
        self.foodTotal = NutritionValues(0, 0, 0, 0, 0, 1)
    
    def print(self, output):
        self.foodTotal = NutritionValues(0, 0, 0, 0, 0, 1)
        self.foodTotal = self.foodItem.nutritionValue.addNutritionValues(self.amount, self.foodTotal)
        output += "\t{0} [{1}g]:\n".format(self.foodItem.name, self.amount)   
        output = self.foodTotal.print(output)
        
        return output

class Meal:
    def __init__(self, name, mealItems):
        self.mealItems = mealItems
        self.name = name
        self.mealTotal = self.getTotalNutritionValue()        
        
    def getTotalNutritionValue(self):
        mealTotal = NutritionValues(0, 0, 0, 0, 0, 1)

        for m in self.mealItems:
           mealTotal = m.foodItem.nutritionValue.addNutritionValues(m.amount, mealTotal)
        
        return mealTotal
    
    def print(self, output):
        output += "{0}:\n".format(self.name)
        for m in self.mealItems:
            output = m.print(output)
        output += "----------{0} total:----------\n".format(self.name)
        output = self.mealTotal.print(output)
        
        return output
    
class DayOfEating:
    def __init__(self, name, meals):
        self.meals = meals
        self.name = name
        self.dayTotal = self.getTotalNutritionValue()       
    
    def getTotalNutritionValue(self):
        dayTotal = NutritionValues(0, 0, 0, 0, 0, 1)

        for m in self.meals:
            mealTotal = m.getTotalNutritionValue()
            dayTotal = mealTotal.addNutritionValues(1, dayTotal)
        
        return dayTotal
    
    def print(self):
        d.getTotalNutritionValue()
        output = ""
        for m in self.meals:
            output = m.print(output)
        
        output += "!!!!!!!!!!Gesamt:!!!!!!!!!!\n"
        output = self.dayTotal.print(output)
        print(output)
        
        with open("{0}.txt".format(self.name), "w") as text_file:
            text_file.write(output)

db = FoodItemsDatabase();   
 
m1 = Meal("Fruehstueck", [
        MealItem(db.getByName("Haferflocken"), 150), 
        MealItem(db.getByName("Leinsamen"), 30),
        MealItem(db.getByName("EiProtein"), 20)
        ]
)

m2 = Meal("Mittag", [
	MealItem(db.getByName("Kabeljau"), 250),
	MealItem(db.getByName("Brokkoli"), 250),
	MealItem(db.getByName("Mandeln"), 50),
        ]
)

m3 = Meal("Mittag2", [
	MealItem(db.getByName("Maiswaffeln"), 100),
	MealItem(db.getByName("Erdnussmus"), 50),
        ]
)

m4 = Meal("Abend", [
	MealItem(db.getByName("Haehnchenbrust"), 200),
	MealItem(db.getByName("Kaisergemuese"), 250),
	MealItem(db.getByName("Apfel"), 150),
        ]
)

m5 = Meal("Nacht", [
	MealItem(db.getByName("Quark"), 500),
        ]
)

currentDate = date.today().strftime("%b_%d_%Y")
d = DayOfEating(currentDate, [ m1, m2, m3, m4, m5 ])

d.print()

#	MealItem(db.getByName("Haferflocken"), 100),
#	MealItem(db.getByName("Mandeln"), 60),
#	MealItem(db.getByName("EiProtein"), 75),
#	MealItem(db.getByName("Bananen"), 150),
#	MealItem(db.getByName("Apfel"), 150),
#	MealItem(db.getByName("Ei"), 107),
#	MealItem(db.getByName("Quark"), 250),
