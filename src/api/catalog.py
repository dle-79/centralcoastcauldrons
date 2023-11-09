from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    with db.engine.begin() as connection:
        potions = connection.execute(sqlalchemy.text("SELECT * from potions")).all()

    # Can return a max of 20 items.
    catalog = []
    count = 0

    for potion in potions:
        if count >= 20:
            break

        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("SELECT SUM(potion_change) AS quantity FROM account_potion_ledger_entries WHERE potion_id = :potion_id"),
            [{"potion_id": potion.id}]).first()

        quant = result.quantity
        if quant is None:
            quant = 0
        
        if quant != 0:
            catalog.append({
                    "sku": potion.sku,
                    "name": potion.name,
                    "quantity": quant,
                    "price": potion.price,
                    "potion_type": [potion.num_red_ml, potion.num_green_ml, potion.num_blue_ml, potion.num_dark_ml],
                })
            count += 1
    if len(catalog) == 0:
        return []
    print(catalog)   
    return catalog



