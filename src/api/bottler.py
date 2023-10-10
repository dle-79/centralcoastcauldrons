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
        redML = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory;"))

    if 100 * potions_delivered[0].quantity > int(redML):
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - " 
            + str(100 * potions_delivered[0].quantity) + ", num_red_potions = num_red_potions + "
            + str(potions_delivered[0].quantity) + ";"))
    

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

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": bottle,
            }
        ]
    
