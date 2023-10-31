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

    if (len(barrels_delivered) == 0):
        return "ok"
    
    gold_paid = 0
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
        id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO account_transactions (description)
                VALUES (purchased :red_ml red ml, :green_ml green ml, :blue_ml blue ml, 
                and :dark_ml dark ml for :gold gold)
                RETURNING id
                """),
                [{"red_ml": red_ml,
                "green_ml": green_ml,
                "blue_ml": blue_ml,
                "dark_ml": dark_ml,
                "gold": gold_paid}]  
            ).scalar_one()

        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO account_ml_ledger_entry (id, red_ml_change, green_ml_change, blue_ml_change, dark_ml_change)
                VALUES (:id, :red_ml, :green_ml, :blue_ml, :dark_ml)
                """),
                [{"id": id,
                "red_ml": red_ml,
                "green_ml": green_ml,
                "blue_ml": blue_ml,
                "dark_ml": dark_ml}] 
            ) 

        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO account_gold_ledger_entry (id, gold_change)
                VALUES (:id, :gold)
                """),
                [{"id": id,
                "gold": gold_paid}]
            )
    return "OK"

        
    
    
    

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""SELECT SUM(gold_change) AS gold FROM account_gold_ledger_entries""")).first()
        gold = result.gold

        result = connection.execute(sqlalchemy.text("""SELECT SUM(red_ml_change) AS red, SUM(green_ml_change) AS green,
        SUM(blue_ml_change) AS blue, SUM(dark_ml_change) AS dark FROM account_ml_ledger_entries""")).first()
        red = result.red
        green = result.green
        blue = result.blue
        dark = result.dark
    
    if red is None:
        red = 0

    if green is None:
        green = 0

    if blue is None:
        blue = 0
    
    if dark is None:
        dark = 0

    if gold is None:
        gold = 0


    purchase = []
    gold_spent = 0


    for barrel in wholesale_catalog:
        quantity = 0
        if barrel.potion_type == [1, 0, 0, 0] and red < 500:
            quantity = min(barrel.quantity, gold//barrel.price)
            gold_spent += barrel.price * quantity
            red += barrel.ml_per_barrel * quantity
        elif barrel.potion_type == [0, 1, 0, 0] and green < 500:
            quantity = min(barrel.quantity, gold//barrel.price)
            gold_spent += barrel.price * quantity
            green += barrel.ml_per_barrel * quantity
        elif barrel.potion_type == [0, 0, 1, 0] and blue < 500:
            quantity = min(barrel.quantity, gold//barrel.price)
            gold_spent += barrel.price * quantity
            blue += barrel.ml_per_barrel * quantity
        elif barrel.potion_type == [0, 0, 0, 1] and dark < 500:
            quantity = min(barrel.quantity, gold//barrel.price)
            gold_spent += barrel.price * quantity
            dark += barrel.ml_per_barrel * quantity

        if gold_spent <= gold and quantity != 0:
            purchase.append({
                    "sku": barrel.sku,
                    "quantity": quantity,
                })
    
    print(purchase)
    return purchase
                
            


        
    


