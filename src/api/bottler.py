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

    additional_potions = sum(potion.quantity for potion in potions_delivered)
    red_ml = sum(potion.quantity * potion.potion_type[0] for potion in potions_delivered)
    green_ml = sum(potion.quantity * potion.potion_type[1] for potion in potions_delivered)
    blue_ml = sum(potion.quantity * potion.potion_type[2] for potion in potions_delivered)
    dark_ml = sum(potion.quantity * potion.potion_type[3] for potion in potions_delivered)

    with db.engine.begin() as connection:
    
        
        for potion in potions_delivered:
            connection.execute(
                sqlalchemy.text("""
                UPDATE potions
                SET inventory = inventory + :additional_potions
                WHERE type = :potion_type"""),
                [{"additional_potions": potion.quantity,
                "potion_type": potion.potion_type}]
            )

            connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO account_transactions (description)
                VALUES (used :red_ml red ml, :green_ml green ml, :blue_ml blue ml, 
                and :dark_ml dark ml to make :num potion)
                """),
                [{"red_ml": red_ml,
                "green_ml": green_ml,
                "blue_ml": blue_ml,
                "dark_ml": dark_ml,
                "num": additional_potions}]  
            )

            connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO account_ml_ledger_entry (red_ml_change, green_ml_change, blue_ml_change, dark_ml_change)
                VALUES (:red_ml, :green_ml, :blue_ml, :dark_ml)
                """),
                [{"red_ml": red_ml * -1,
                "green_ml": green_ml * -1,
                "blue_ml": blue_ml * -1,
                "dark_ml": dark_ml * -1}] 
            )

            connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO account_potion_ledger_entry (potion_change, potion_type)
                VALUES (:potions, :potion_type)
                )
                """),
                [{"potions": potion.quantity,
                "potion_type": potion.potion_type}] 
            )



    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""SELECT SUM(*) AS gold FROM account_ml_ledger_entries"""))
        red_ml = result.first().red_ml_change
        green_ml = result.first().green_ml_change
        blue_ml = result.first().blue_ml_change
        dark_ml = result.first().dark_ml_change

        potions = connection.execute(sqlalchemy.text("SELECT * FROM potions")).all()

    
    bottles = []
    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    for potion in potions:
        inventory = potion.inventory
        bottled = False
        red_bot = 10000
        green_bot = 10000
        blue_bot = 10000
        dark_bot = 10000

        if (red_ml >= potion.num_red_ml and green_ml >= potion.num_green_ml and blue_ml >= potion.num_blue_ml and dark_ml >= potion.num_dark_ml ):
            if (potion.num_red_ml != 0):
                red_bot = red_ml//potion.num_red_ml
            if (potion.num_green_ml != 0):
                green_bot = green_ml//potion.num_green_ml
            if (potion.num_blue_ml != 0):
                blue_bot = blue_ml//potion.num_blue_ml
            if (potion.num_dark_ml != 0):
                dark_bot = dark_ml//potion.num_dark_ml
            inventory += min(red_bot, green_bot, blue_bot, dark_bot)
            bottled = True
            
        
        if bottled == True:
            bottles.append(
                {"potion_type": [potion.num_red_ml, potion.num_green_ml, potion.num_blue_ml, potion.num_dark_ml],
                "quantity": inventory}
            )