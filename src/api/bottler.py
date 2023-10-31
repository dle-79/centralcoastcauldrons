from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print(potions_delivered)

    if (len(potions_delivered) == 0):
        return "ok"

    with db.engine.begin() as connection:
    
        
        for potion in potions_delivered:
            red_ml = potion.potion_type[0]
            green_ml = potion.potion_type[1]
            blue_ml = potion.potion_type[2]
            dark_ml = potion.potion_type[3]


        id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO account_transactions (description)
                VALUES (made :quantity potion that are [:red_ml, :green_ml, :blue_ml, :dark_ml])
                RETURNING id
                """),
                [{"red_ml": red_ml,
                "green_ml": green_ml,
                "blue_ml": blue_ml,
                "dark_ml": dark_ml,
                "quantity": potion.quantity}]  
            ).scalar_one()

        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO account_ml_ledger_entry (id, red_ml_change, green_ml_change, blue_ml_change, dark_ml_change)
                VALUES (:id, :red_ml, :green_ml, :blue_ml, :dark_ml)
                """),
                [{"id": id,
                "red_ml": red_ml * -potion.quantity,
                "green_ml": green_ml * -potion.quantity,
                "blue_ml": blue_ml * -potion.quantity,
                "dark_ml": dark_ml * -potion.quantity}] 
            ) 

        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO account_potion_ledger_entry (id, potion_change, potion_sku)
                SELECT :id, :quantity, potions.sku
                FROM potions
                WHERE potions.num_red = :red_ml, potions.num_green = :green_ml,
                potions.num_blue = :blue_ml, potions.num_dark = :dark_ml
                """),
                [{"id": id,
                "quantity": potion.quantity,
                "red_ml": red_ml,
                "green_ml": green_ml,
                "blue_ml": blue_ml,
                "dark_ml": dark_ml}]
            )
    return "OK"



    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""SELECT SUM(red_ml_change) AS red_ml,
        SUM(green_ml_change) AS green_ml,
        SUM(blue_ml_change) AS blue_ml,
        SUM(dark_ml_change) AS dark_ml
        FROM account_ml_ledger_entries""")).first()
        red_ml = result.red_ml
        green_ml = result.green_ml
        blue_ml = result.blue_ml
        dark_ml = result.dark_ml

        potions = connection.execute(sqlalchemy.text("SELECT * FROM potions")).all()

    if red_ml is None:
        red_ml = 0

    if green_ml is None:
        green_ml = 0

    if blue_ml is None:
        blue_ml = 0
    
    if dark_ml is None:
        dark_ml = 0
    
    bottles = []
    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    for potion in potions:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("""SELECT SUM(potion_change) AS potion_quant FROM account_potion_ledger_entries WHERE potion_sku = :potion_sku"""),
            [{"potion_sku": potion.potion_sku}]).first()
        quant = result.potion_quant
        new_bottles = 0
        bottled = False
        red_bot = 10000
        green_bot = 10000
        blue_bot = 10000
        dark_bot = 10000

        if (red_ml >= potion.num_red_ml and green_ml >= potion.num_green_ml and blue_ml >= potion.num_blue_ml and dark_ml >= potion.num_dark_ml and quant < 5):
            if (potion.num_red_ml != 0):
                red_bot = red_ml//potion.num_red_ml
            if (potion.num_green_ml != 0):
                green_bot = green_ml//potion.num_green_ml
            if (potion.num_blue_ml != 0):
                blue_bot = blue_ml//potion.num_blue_ml
            if (potion.num_dark_ml != 0):
                dark_bot = dark_ml//potion.num_dark_ml
            new_bottles = min(red_bot, green_bot, blue_bot, dark_bot)
            red_ml -= potion.num_red_ml * new_bottles
            green_ml -= potion.num_green_ml * new_bottles
            blue_ml -= potion.num_blue_ml * new_bottles
            dark_ml -= potion.num_dark_ml * new_bottles
            bottled = True
            
        
        if bottled == True:
            bottles.append(
                {"potion_type": [potion.num_red_ml, potion.num_green_ml, potion.num_blue_ml, potion.num_dark_ml],
                "quantity": new_bottles + quant}
            )
    
    if len(bottles)== 0:
        return []
    return bottles