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
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory;"))
    
    first_row = result.first()

    if first_row.num_red_potions < 10 & first_row.gold > barrels_delivered[0].price:
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - " 
            + str(barrels_delivered[0].price) + ", num_red_ml +"  + str(barrels_delivered[0].ml_per_barrel) + ";"))
    
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    with db.engine.begin() as connection:
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory;"))

    for barrel in wholesale_catalog:
        if barrel.sku == "SMALL_RED_BARREL" & barrel.price < gold:
            return [
                {
                    "sku": "SMALL_RED_BARREL",
                    "quantity": 1,
                }
            ]
        
    if barrel.sku == "SMALL_RED_BARREL" & barrel.price < gold:
            return [
                {
                    "sku": "SMALL_RED_BARREL",
                    "quantity": 0,
                }
            ]


