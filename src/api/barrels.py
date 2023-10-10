from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str
    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory;"))
        gold = result.first().gold
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory;"))
        num_red = result.first().num_red_potions
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory;"))
        num_green = result.first().num_green_potions
        result = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory;"))
        num_blue = result.first().num_blue_potions

    for barrel in barrels_delivered:
        if gold < barrel.price:
            return "not enough gold"
        elif num_red < 10 and gold >= barrel.price and "RED" in barrel.sku:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - " 
                + str(barrel.price) + ", num_red_ml = num_red_ml + "  + str(barrel.ml_per_barrel) + ";")
            return "ok"
        elif num_green < 10 and gold >= barrel.price and "GREEN" in barrel.sku:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - " 
                + str(barrel.price) + ", num_green_ml = num_green_ml + "  + str(barrel.ml_per_barrel) + ";")
            return "ok"
        elif num_blue < 10 and gold >= barrel.price and "BLUE" in barrel.sku:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - " 
                + str(barrel.price) + ", num_blue_ml = num_blue_ml + "  + str(barrel.ml_per_barrel) + ";")
            return "ok"
        else:
            return "incorrect sku"
        
    

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory;"))
        gold = result.first().gold
    

    purchase = []


    for barrel in wholesale_catalog:
        if barrel.price <= gold:
            purchase.append({
                    "sku": barrel.sku,
                    "quantity": barrel.quantity,
                })
    
    return purchase
                
            


        
    


