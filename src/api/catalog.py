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
        potions = connection.execute(sqlalchemy.text("SELECT * from potions where inventory != 0")).all()

    # Can return a max of 20 items.
    catalog = []

    for potion in potions:
        catalog.append({
                "sku": potion.sku,
                "name": potion.name,
                "quantity": potion.inventory,
                "price": potion.price,
                "potion_type": [potion.num_red_ml, potion.num_green_ml, potion.num_blue_ml, potion.num_dark_ml],
            })
    
    return catalog



