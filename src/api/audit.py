from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""SELECT SUM(gold_change) AS gold FROM account_gold_ledger_entries"""))
        gold = result.first().gold

        result = connection.execute(sqlalchemy.text("""SELECT SUM(red_ml_change) AS red, SUM(green_ml_change) AS green, SUM(blue_ml_change) AS blue,
        SUM(dark_ml_change) AS dark
        FROM account_ml_ledger_entries"""))
        red_ml = result.first().red
        green_ml = result.first().green
        blue_ml = result.first().blue
        dark_ml = result.first().dark

        result = connection.execute(sqlalchemy.text("""SELECT SUM(potion_change) AS potion FROM account_potion_ledger_entries"""))
        potion = result.first().potion
    
    return {"number_of_potions": potion, "ml_in_barrels": red_ml + green_ml + blue_ml + dark_ml, "gold": gold}

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
