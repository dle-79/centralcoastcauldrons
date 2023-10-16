from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
from src import database as db

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory;"))
        gold = result.first().gold

        result = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory;"))
        red = result.first().num_red_potions

        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory;"))
        green = result.first().num_green_potions

        result = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory;"))
        blue = result.first().num_blue_potions

        result = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory;"))
        red_ml = result.first().num_red_ml

        result = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory;"))
        green_ml = result.first().num_green_ml

        result = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory;"))
        blue_ml = result.first().num_blue_ml
    
    return {"number_of_potions": red+green+blue, "ml_in_barrels": red_ml + green_ml + blue_ml, "gold": gold}

class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    """ """
    print(audit_explanation)

    return "OK"
