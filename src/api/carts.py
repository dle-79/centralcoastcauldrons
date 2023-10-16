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
    cart[cart_id] = {"name": new_cart.customer, 
    "red": 0, 
    "green": 0, 
    "blue": 0, 
    "cost": 0, 
    "checkout": False}
    return {"cart_id": cart_id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """

    return {"id": cart_id, 
    "name": cart[cart_id]["name"],
    "red": cart[cart_id]["red"], 
    "green": cart[cart_id]["green"], 
    "blue": cart[cart_id]["blue"], 
    "cost": cart[cart_id]["cost"], 
    "checkout": cart[cart_id]["checkout"]}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    
    if item_sku == "RED_POTION_0":
        cart[cart_id]["red"] += cart_item.quantity
        cart[cart_id]["gold"] += cart_item.quantity
        return "OK"
    elif item_sku == "GREEN_POTION_0":
        cart[cart_id]["green"] += cart_item.quantity
        cart[cart_id]["gold"] += cart_item.quantity
        return "OK"
    elif item_sku == "BLUE_POTION_0":
        cart[cart_id]["blue"] += cart_item.quantity
        cart[cart_id]["gold"] += cart_item.quantity
        return "OK"
    else:
        return "no item"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
        num_red = result.first().num_red_potions
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        num_green = result.first().num_green_potions
        result = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory"))
        num_blue = result.first().num_blue_potions

    red_purchase = cart[cart_id]["red"]
    green_purchase = cart[cart_id]["green"]
    blue_purchase = cart[cart_id]["blue"]
    gold_purchase = cart[cart_id]["gold"]

    if num_red < red_purchase or num_green < green_purchase or num_blue < blue_purchase:
        return "potions unavailable"
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = num_red_potions - " + str(red_purchase) + 
        ", num_green_potions = num_green_potions - " + str(green_purchase) + ", num_blue_potions = num_blue_potions - " +
        str(blue_purchase) + ", gold = gold + " + str(gold_purchase)))

    return {"total_potions_bought": red_purchase + green_purchase + blue_purchase, "total_gold_paid": gold_purchase}
