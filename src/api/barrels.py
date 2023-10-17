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
    
    gold = 0
    red_ml = 0
    green_ml = 0
    blue_ml = 0
    dark_ml = 0

    for barrel in barrels_delivered:
        gold_paid += barrel.price*barrel.quantity
        if barrel.potion_type == [1, 0, 0, 0]:
            red_ml += barrel.ml_per_barrel * barrel.quantity
        elif barrel.potion_type == [0, 1, 0, 0]:
            green_ml += barrel.ml_per_barrel * barrel.quantity
        elif barrel.potion_type == [0, 0, 1, 0]:
            blue_ml += barrel.ml_per_barrel * barrel.quantity
        elif barrel.potion_type == [0, 0, 0, 1]:
            dark_ml += barrel.ml_per_barrel * barrel.quantity
        else:
            raise Exception("invalid type")
    
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE global_inventory 
                SET red_ml = red_ml + :red_ml,
                green_ml = green_ml + :green_ml,
                blue_ml = blue_ml + :blue_ml,
                dark_ml = dark_ml + :dark_ml,
                gold = gold - :gold
                """),
                [{"red_ml": red_ml,
                "green_ml": green_ml,
                "blue_ml": blue_ml,
                "dark_ml": dark_ml,
                "gold": gold}]
                
            )
    return "OK"

        
    
    
    

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""SELECT * FROM global_inventory"""))
        gold = result.first().gold
        red = result.first().num_red_ml
        green = result.first().num_green_ml
        blue = result.first().num_blue_ml
        dark = result.first().num_dark_ml


    purchase = []
    gold_spent = 0


    for barrel in wholesale_catalog:
        quantity = 0
        if barrel.potion_type == [1, 0, 0, 0] and red < 500:
            quantity = min(barrel.quantity, gold//barrel.price)
            gold_spent += barrel.price * quantity
        elif barrel.potion_type == [0, 1, 0, 0] and green < 500:
            quantity = min(barrel.quantity, gold//barrel.price)
            gold_spent += barrel.price * quantity
        elif barrel.potion_type == [0, 0, 1, 0] and blue < 500:
            quantity = min(barrel.quantity, gold//barrel.price)
            gold_spent += barrel.price * quantity
        elif barrel.potion_type == [0, 0, 0, 1] and dark < 500:
            quantity = min(barrel.quantity, gold//barrel.price)
            gold_spent += barrel.price * quantity

        if gold_spent <= gold:
            purchase.append({
                    "sku": barrel.sku,
                    "quantity": quantity,
                })
    
    print(purchase)
    return purchase
                
            


        
    


