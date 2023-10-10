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
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory;"))
        red_ml = result.first().num_red_ml

        result = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory;"))
        green_ml = result.first().num_green_ml

        result = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory;"))
        blue_ml = result.first().num_blue_ml

    for potion in potions_delivered:
        if 100 * potion.quantity >= int(red_ml) and potion.potion_type[0] == 100:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - " 
                + str(100 * potion.quantity) + ", num_red_potions = num_red_potions + "
                + str(potion.quantity) + ";"))
        if 100 * potion.quantity >= int(green_ml) and potion.potion_type[1] == 100:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml - " 
                + str(100 * potion.quantity) + ", num_green_potions = num_green_potions + "
                + str(potion.quantity) + ";"))
        if 100 * potion.quantity >= int(blue_ml) and potion.potion_type[2] == 100:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = num_blue_ml - " 
                + str(100 * potion.quantity) + ", num_blue_potions = num_blue_potions + "
                + str(potion.quantity) + ";"))
        if potion.quantity == 0:
            return "no mL"
    

    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory;"))
        red_ml = result.first().num_red_ml

        result = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory;"))
        green_ml = result.first().num_green_ml

        result = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory;"))
        blue_ml = result.first().num_blue_ml
    
    red_bottle = red_ml//100
    green_bottle = green_ml//100
    blue_bottle = blue_ml//100

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    if red_bottle == 0 and green_bottle == 0 and blue_bottle == 0:
            return "no ml to bottle"
    elif red_bottle > 0:
        return [
                {
                    "potion_type": [100, 0, 0, 0],
                    "quantity": red_bottle,
                }
            ]
    elif green_bottle > 0:
        return [
                {
                    "potion_type": [0, 100, 0, 0],
                    "quantity": green_bottle,
                }
            ]
    else:
        return [
                {
                    "potion_type": [0, 0, 100, 0],
                    "quantity": blue_bottle,
                }
            ]

    
