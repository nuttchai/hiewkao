import json 
import time
from flask import Flask, redirect, render_template, url_for, jsonify, request
from flaskext.mysql import MySQL
from calculaterate import calRate

app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_HOST'] = '34.126.95.175'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'lengmaynut123'
app.config['MYSQL_DATABASE_DB'] = 'Project'

mysql.init_app(app)

# cursor
con = mysql.connect()
cursor = con.cursor()

# cursor = mysql.get_db().cursor()

class RequireItem:

    def __init__(self, customerid=None, menuid=None, chefname=None, menuname=None,  selectFridge=None, allIngredient=None, selectIngredient=None, userRate=-1, status=False):
        self.customerid         = customerid
        self.menuid             = menuid
        self.menuname           = menuname
        self.chefname           = chefname
        self.selectFridge       = selectFridge
        self.allIngredient      = allIngredient
        self.selectIngredient   = selectIngredient
        self.userRate           = userRate  
        self.status             = status

usageInfo = RequireItem()


######################### HOME PAGE #########################


# User home page 
@app.route('/')
def userSetup():

    global usageInfo
    usageInfo.customerid = 'US0001'

    return redirect(url_for("homePage"))


@app.route('/homePage')
def homePage():

    return render_template('homePage.html', name='User01')


# frige selection page (can select cook or edit mode)
@app.route('/fridgeSelection', methods=['GET'])
def displayFridge():
    
    # Find all possible menu from customerid
    global usageInfo
    sql = "SELECT Refrigerator_ID, Refrigerator_Name FROM CustomerRefrigerator WHERE Customer_ID = '" + str(usageInfo.customerid +"'")
    cursor.execute(sql)
    fridgeResult = cursor.fetchall() 
    
    return render_template('fridge.html', fridges=fridgeResult)


######################### COOKING PART #########################


@app.route('/fridgeSelection/ingredient', methods=['GET', 'POST'])
def displayIngredient():

    global usageInfo
    listIngredient = usageInfo.allIngredient

    return render_template('ingredient.html', ingredients=listIngredient)


@app.route('/fridgeSelection/ingredient/checkIngre', methods=['GET', 'POST'])
def checkIngredient():

    if request.method == 'POST':
        if request.form.getlist('checkbox'):

            confirmIngredient = request.form.getlist('checkbox')   
            global usageInfo
            usageInfo.selectIngredient = confirmIngredient

            # for making 2 instances on each row
            conIngreWithStep = []
            step = 0
            for each in confirmIngredient:
                conIngreWithStep.append({"ingredient": each, "step": step})
                if step == 0: step = 1
                else: step = 0

            return render_template('checkIngredient.html', ingredients=conIngreWithStep)
        
    else: return "Error (No POST:checkIngredient)"


@app.route('/fridgeSelection/ingredient/resultmenu', methods=['GET', 'POST'])
def displayMenu():
    
    global usageInfo
    # Get All Confirmed Ingredient From confirmIngre
    selectIngredient = usageInfo.selectIngredient
    available_menu = []

    sql = "SELECT * FROM MenuList"  
    cursor.execute(sql)
    results = cursor.fetchall()

    for result in results: 
        
        menu_ingredient = json.loads(result[3])
        check_ingredient = []

        for each in menu_ingredient["ingredient"]:
            check_ingredient.append(each[0])

        # Check that all ingredient from check_ingredient are in selected_ingredient
        checkIngre = all(item in selectIngredient for item in check_ingredient) 
        if checkIngre: available_menu.append(result)

        detail = []
        for eachMenu in available_menu:
            rate = json.loads(eachMenu[8])
            if rate['rate'] == []: avgRate = "-"
            else: avgRate = rate['avgRate']
            detail.append({"FoodID":eachMenu[0], "menuName":eachMenu[2] , "Rate": avgRate})
    
    return render_template("availableMenu.html", listMenu=detail)


@app.route('/fridgeSelection/ingredient/resultmenu/recipe', methods=['GET', 'POST'])
def displayRecipe():

    if request.method == 'POST':
        # Display menuID From a Selected Menu

        menuID = request.form.get('selectMenu')
        sql = "SELECT * FROM MenuList WHERE food_id = '"+ menuID +"'"
        cursor.execute(sql)
        menuData = cursor.fetchone() 
        
        global usageInfo
        usageInfo.menuid    = menuID
        usageInfo.menuname  = menuData[2]
        usageInfo.chefname  = menuData[1]

        menuInfo = {}
        menuInfo["menu"] = usageInfo.menuname
        menuInfo["chef"] = usageInfo.chefname
        menuInfo["ingr"] = json.loads(menuData[3])["ingredient"]
        menuInfo["step"] = json.loads(menuData[4])["step"]
        menuInfo["price"] = menuData[5]
        menuInfo["vdo"]  = menuData[6]
        menuInfo["pic"]  = menuData[7]
        menuInfo["rate"] = json.loads(menuData[8])["avgRate"]
        menuInfo["desc"] = menuData[9]

        return render_template("menurecipe.html", menuInfo=menuInfo)


@app.route('/fridgeSelection/ingredient/resultmenu/recipe/finish', methods=['GET', 'POST'])
def done():

    if request.method == 'POST':
    
        detail = request.form.get('finishButton')
        global usageInfo
        usageInfo.status = True 
        return render_template("ratingMenu.html", chefname=usageInfo.chefname, menuname=usageInfo.menuname)


@app.route('/fridgeSelection/ingredient/resultmenu/recipe/finish/rateMenu', methods=['GET', 'POST'])
def calculatation():

    if request.form.get('ratingMenu'):
        rate = request.form.get('ratingMenu')

        # Store Rate Data
        global usageInfo
        usageInfo.userRate = rate
        
        # Query Information
        sql = "SELECT * FROM MenuList WHERE food_id = '"+ str(usageInfo.menuid) +"'"
        cursor.execute(sql)
        menuDetail = cursor.fetchone() 

        # Calculate Remaining Ingredient 
        # Convert Str to Dict
        ingredientUsageDetail = json.loads(menuDetail[3]) # format => {"Rice": 200, "Egg": 2}
        ## Wait

        # Calculate Rate
        # Convert Str into Dict
        rateDetail = json.loads(menuDetail[8]) # format => {"rate": [], "avgRate":""}
        
        # Calculate New Rate
        newRateDetail = calRate(rateDetail, rate)
        strRateDetail = json.dumps(newRateDetail)

        # Update Value
        sql = "UPDATE MenuList SET rate = '" + strRateDetail + "' WHERE food_id = '"+ str(usageInfo.menuid)+ "'"
        cursor.execute(sql)
        con.commit()
        
    else: print("no Vote")

    return redirect(url_for('homePage'))


######################### EDIT INGREDIENT IN FRIDGE #########################

@app.route('/fridgeSelection/edit/displayIngredient', methods=['GET', 'POST'])
def displayIngredientEdit():

    global usageInfo
    listIngredient = usageInfo.allIngredient

    listIngredientwithStep = []

    for each in listIngredient:
        listIngredientwithStep.append({"IngreName": each[0], "Type": each[1]})

    return render_template('ingredientEdit.html', ingredients=listIngredientwithStep)


@app.route('/fridgeSelection/edit/displayIngredient/addIngre', methods=['GET', 'POST'])
def addIngre():

    sql = "SELECT * FROM IngredientList ORDER BY Type ASC"
    cursor.execute(sql)
    allIngredient = cursor.fetchall()

    locType, check, position = [], '', 0
    for ingre in allIngredient:

        if ingre[3] != check: 
            locType.append(position)

        position += 1
        check = ingre[3]

    return render_template('addIngredient.html', ingredients=allIngredient, locType=locType)


@app.route('/fridgeSelection/edit/displayIngredient/removeIngre', methods=['GET', 'POST'])
def removeIngre():
    
    selectFridge = usageInfo.selectFridge
    # Find Refrigerator_ID by using its name
    sql = "SELECT Refrigerator_ID FROM CustomerRefrigerator WHERE Refrigerator_Name = '"+ str(selectFridge) + "'" 
    cursor.execute(sql)
    fridgeID = cursor.fetchone()[0] # get name

    # Find all possible ingredients in that Refrigerator through its ID
    sql = "SELECT Remaining_Ingredient, Type FROM Refrigerator WHERE Refrigerator_ID = '"+ str(fridgeID) + "' ORDER BY Type ASC" 
    cursor.execute(sql)
    listIngredient = cursor.fetchall()

    return render_template('removeIngredient.html', ingredients=listIngredient)


@app.route('/fridgeSelection/edit/displayIngredient/done', methods=['GET', 'POST'])
def editingIngredient():

    global usageInfo

    if request.method == 'POST':

        if request.form.getlist('removeCheckbox'):

            removeIngre = request.form.getlist('removeCheckbox')
            sql = "SELECT Refrigerator_ID FROM CustomerRefrigerator WHERE Refrigerator_Name = '"+ str(usageInfo.selectFridge) + "'" 
            cursor.execute(sql)
            fridgeID = cursor.fetchone()[0] # get ID name
            text = ""

            for eachIngre in removeIngre:
                if eachIngre != removeIngre[-1]: text += " (Remaining_Ingredient = '"+ str(eachIngre) + "') OR"
                else: text += " (Remaining_Ingredient = '"+ str(eachIngre) + "')"

            sql = "DELETE FROM Refrigerator WHERE" + text
            cursor.execute(sql)
            con.commit()

            # Update Ingredient In Variable
            sql = "SELECT Remaining_Ingredient, Type FROM Refrigerator WHERE Refrigerator_ID = '"+ str(fridgeID) + "' ORDER BY Type ASC" 
            cursor.execute(sql)
            listIngredient = cursor.fetchall()
            usageInfo.allIngredient = listIngredient

        elif request.form.getlist('addCheckbox'): 
            
            addIngre = request.form.getlist('addCheckbox')
            sql = "SELECT Refrigerator_ID FROM CustomerRefrigerator WHERE Refrigerator_Name = '"+ str(usageInfo.selectFridge) + "'" 
            cursor.execute(sql)
            fridgeID = cursor.fetchone()[0] # get ID name

            text = ''          
            defualtNumber = 10 # Edit Later On

            for eachIngreID in addIngre:
                if eachIngreID != addIngre[-1]: text += " (Ingredient_ID = '"+ str(eachIngreID) + "') OR"
                else: text += " (Ingredient_ID = '"+ str(eachIngreID) + "')"

            sql = "SELECT * FROM IngredientList WHERE" + text
            cursor.execute(sql)
            selectedIngre = cursor.fetchall()
            
            # Remove the ingredient that already have in fridge
            sqlGetFridgeIngre = "SELECT Ingredient_ID FROM Refrigerator WHERE Refrigerator_ID = '" + fridgeID + "'"
            cursor.execute(sqlGetFridgeIngre)
            fridgeIngre = cursor.fetchall()

            # Put in list
            listFridgeIngre = []
            for each in fridgeIngre: listFridgeIngre.append(each[0])

            # Store in DB
            sql = "INSERT INTO Refrigerator (Refrigerator_ID, Ingredient_ID, Remaining_Ingredient, Remaining_Number, Type) VALUES (%s, %s, %s, %s, %s)" 
            availableIngre = []

            for info in selectedIngre:
                if info[0] not in listFridgeIngre: 
                    availableIngre.append((fridgeID, info[0], info[1], defualtNumber, info[3]))

            cursor.executemany(sql, availableIngre)
            con.commit()

            # Update Ingredient In Variable
            sql = "SELECT Remaining_Ingredient, Type FROM Refrigerator WHERE Refrigerator_ID = '"+ str(fridgeID) + "' ORDER BY Type ASC" 
            cursor.execute(sql)
            listIngredient = cursor.fetchall()
            usageInfo.allIngredient = listIngredient

    return redirect(url_for('displayIngredientEdit'))


######################### NAVIGATE TO SELECTED MODE #########################

@app.route('/fridgeSelection/selectMode', methods=['GET', 'POST'])
def navigateMode():
    
    if request.method == 'POST':
        
        selectFridge = request.form.get('selectFridge')
        global usageInfo
        # Declare Fridge that user select
        usageInfo.selectFridge = selectFridge

        # Find Refrigerator_ID by using its name
        sql = "SELECT Refrigerator_ID FROM CustomerRefrigerator WHERE Refrigerator_Name = '"+ str(selectFridge) + "'" 
        cursor.execute(sql)
        fridgeID = cursor.fetchone()[0] # get name

        # Find all possible ingredients in that Refrigerator through its ID
        sql = "SELECT Remaining_Ingredient, Type FROM Refrigerator WHERE Refrigerator_ID = '"+ str(fridgeID) + "' ORDER BY Type ASC" 
        cursor.execute(sql)
        listIngredient = cursor.fetchall()
        usageInfo.allIngredient = listIngredient

        # Navigate to a given route
        if request.form['submit_button'] == 'cook': return redirect(url_for('displayIngredient'))
        else: return redirect(url_for('displayIngredientEdit'))


######################### COIN SHOP #########################

@app.route('/coinshop', methods=['GET', 'POST'])
def coinshop():
    
    return render_template('coinshop.html')


######################### RUN TASK #########################

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')