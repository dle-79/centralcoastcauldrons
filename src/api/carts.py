from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class NewCart(BaseModel):
    customer: str

cart = {}
cart_id = 0

@router.post("/")
def create_cart(new_cart: NewCart):
    """ """

    with db.engine.begin() as connection:
        cart_id = connection.execute(sqlalchemy.text("""INSERT INTO cart (name)
        VALUES (:name);
        RETURNING cart_id
        """),
        [{ "name": new_cart.customer}])

    return {"cart_id": cart_id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""SELECT name from cart WHERE cart_id = :cart_id"""),
        [{"cart_id": cart_id}]).first()
        name = result.name
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """SELECT SUM(cart_item.quantity * potions.price) AS gold,
            SUM(cart_item.quantity) AS quant
            FROM cart_item
            JOIN potions
            ON potions.sku = cart_item.potion_sku
            WHERE cart_item.cart_id = :cart_id
            """),
        [{"cart_id": cart_id}]).first()
        quant = result.quant
        gold = gold
    
    if quant is None:
        quant = 0
    if gold is None:
        gold = 0

    return [{"cart_id": cart_id,
    "customer_name": name,
    "total_cost": gold,
    "total_potion_num": quant}]



class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
        SELECT SUM(account_potion_ledger_entries.potion_change) AS quant
        FROM account_potion_ledger_entries
        JOIN potions
        ON account_potion_ledger_entries.sku = potions.sku
        """),
        [{"item_sku": item_sku}]).first()
    
    quant = result.quant
    if quant is None:
        print("no potions")
        return "ok"
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
        INSERT INTO cart_item (cart_id, potion_sku, quantity)
        SELECT :cart_id, account_potion_ledger_entries.sku, :quantity
        FROM account_potion_ledger_entries, potions
        WHERE :quantity <= :potion_quantity and potions.sku = :item_sku
        """),
        [{"cart_id": cart_id, "item_sku": item_sku, "quantity": cart_item.quantity, "potion_quantity": quant}])
    return "OK"
    



class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    with db.engine.begin() as connection:
        cart_items = connection.execute(sqlalchemy.text("""
        SELECT * FROM cart_item
        WHERE cart_id = :cart_id
         """),
        [{"cart_id": cart_id}])
    
    for item in cart_items:
        with db.engine.begin() as connection:
            potion = connection.execute(sqlalchemy.text("""
            SELECT * FROM potions
            WHERE sku = :potion_sku
             """),
            [{"potion_sku": item.potion_sku}]).first()

            trans_id = connection.execute(sqlalchemy.text("""
            INSERT INTO account_transactions (description)
            VALUES ('customer :cust_id bought :quant :sku potions which cost "gold')
            RETURNING transaction_id
             """),
            [{"cust_id": cart_id, "potion_sku": item.potion_sku, "quant": item.quantity, "gold": potion.price * item.quantity}]).scalar_one()

            connection.execute(sqlalchemy.text("""
            INSERT INTO account_gold_ledger_entries (gold, transaction_id)
            VALUES (:gold, :transaction_id)
             """),
            [{"gold": item.quantity * potion.price, "transaction_id": trans_id}])

            connection.execute(sqlalchemy.text("""
            INSERT INTO account_potion_ledger_entries (potion_sku, potion_change, transaction_id)
            VALUES (:sku, :quant, :transaction_id)
             """),
            [{"sku": item.potion_sku, "quant": -item.quantity, "transaction_id": trans_id}])
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
        DELETE FROM cart_item
        WHERE cart_id = :cart_id
        """),
        [{"cart_id": cart_id}])

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
        DELETE FROM cart
        WHERE cart_id = :cart_id
        """),
        [{"cart_id": cart_id}])

    return "purchased"
