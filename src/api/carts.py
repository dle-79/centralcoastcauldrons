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
    global cart_id
    cart_id += 1
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""INSERT INTO cart (cart_id, name)
        VALUES (:cart_id, :name)"""),
        [{"cart_id": cart_id, "name": new_cart.customer}])

    return {"cart_id": cart_id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""SELECT * from cart WHERE cart_id = :cart_id"""),
        [{"cart_id": cart_id}])
        name =result.first().name
        cost = result.first().total_cost
        potions = result.first().num_potions
    
    return [{"cart_id": cart_id,
    "customer_name": name,
    "total_cost": cost,
    "total_potion_num": potions}]



class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
        INSERT INTO cart_item (cart_id, potion_sku, quantity)
        SELECT :cart_id, potions.potion_sku, :quantity
        FROM potions
        WHERE potions.sku = :item_sku and :quantity <= potions.inventory
        """),
        [{"cart_id": cart_id, "item_sku": item_sku, "quantity": cart_item.quantity}])
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
        UPDATE carts
        SET total_potion_num = total_potion_num + :quantity, total_cost = total_cost + (potions.price * :quantity)
        FROM potions
        WHERE potions.sku = :item_sku and :quantity <= potions.inventory
        """),
        [{"cart_id": cart_id, "item_sku": item_sku, "quantity": cart_item.quantity}])
    return "OK"
    



class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
        UPDATE potions
        SET inventory = inventory - cart_item.quantity
        FROM cart_item
        WHERE potions.sku = cart_item.potion_sku :quantity <= potions.inventory
        """),
        [{"cart_id": cart_id}])
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
        UPDATE global_inventory
        SET gold = gold + carts.total_cost
        FROM cart
        WHERE cart.cart_id = :cart_id
        """),
        [{"cart_id": cart_id}])
    
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
