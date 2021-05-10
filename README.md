# ESSENVIA’S backend development hackathon

WALKTHROUGH:
<br>
<li>The Order number(dd_mm_yyy_sl) and Team(based on previous order) is generated for an order when a post request is made to 'add_order'.</li>

<li>A counter is used to add the serial number to the model’s order_num.The counter is checked every time the model is created, set to 0 if there was a difference in the latest model instance’s order_time and today’s date, otherwise it is incremented by 1.</li>

<li>The teams are selected with a double-ended queue.</li>
<li>Added a custom RangeField in models.py to intake distance from 0.1 to 10.0.</li>
<li>Estimated time is calculated with the distance of the customer and return time of the team assigned(checked at the time of adding a new order).**This can be however improved by adding a job scheduler, or at the time of receiving notification from Team.</li>

<li>Add to cart button checks for the item availability by sending a GET request to ‘api/check_inventory/’ with model_num and quantity and add the item with the requested quantity to the cart(ItemIntake from models.py).</li>

<li>If an item is added multiple times the most recent item will be added to cart and previous ones are deleted(add to cart can be disabled here as well).</li>


<li>Once the order is placed the estimated time is added here, with default status to pending.status does not change to delivered automatically since there could be a difference in actual delivery and estimated delivery time {order can be deleted here with DELETE request to the url}.</li>
<li>
Order History {recent orders first} with order_num, total_price, estimated_time can be retrieved from the “api/order_history/” in PDF format.</li>

<br>
API-ENDPOINTS:
</br>
api/add_order/ (AddOrderApi in Views.py)
<li>POST: Adds an Order Instance to the Table and returns it’s order num {order_num}.</li>

<br>api/check_inventory/ (CheckInventoryApi in views.py)
<li>Requires model_num,quantity,order_num.</li>
<li>Returns a message of warning if insufficient data is passed, item is not available or quantity not available.</li>
<li>Returns a message of success by adding items to the cart(creating model instance) if item is available with the required quantity.</li>
<br>api/place_order/<str:order_num> (OrderApi in views.py)<br>
<li> DELETE: deletes the order from the database (also decrements the counter).</li>
<li>**The GET and POST data for this view is however rendered through django inlineformsets.</li>

<br>api/order_history/(OrderHistoryApi in views.py)
<li>GET: returns all the orders(by most recent) for the day with their order_number, total_price,estimated_time in a PDF format with filename of today’s date.</li>

<br>api/check_status/(CheckStatusApi in views.py)
<li>GET:  returns the status of the order.</li>
<li>POST: (with order_num and status{Pending,WithDrawn,Rejected,Delivered}) updates the order status with a response of a message.</li>
