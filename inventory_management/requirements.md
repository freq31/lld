REQUIREMENTS -

1. Design an Inventory Management system - each product is identified by their unique product Id and have to only track the counts of different product. 
2. Throw alerts for low product count. This threshold quantity is configurable and should be specific for each product in each warehouse, and can be updated afterwards.
3. Allow for addition, removal, transfer of a specific product and its specific quantity between warehouses.
4. Increase the count when product arrives and decrease it when it leaves the warehouse. Now the quantities involved here can be a unit or greater than a unit product. 
5. Implement a thread-safe system- concurrent addition/removal/ transfer operations can be done correctly, and invalid operations should be rejected. Transfers between warehouses must be atomic — meaning a transfer should not leave the system in a partial state if something goes wrong mid-operation.

Error Handling -
1. Removal or transfer of invalid product (not present in inventory) - Rejection of request which removes/ transfer a product which already not present in any warehouse.
2. Addition/ Removal/ Transfer of product to invalid warehouse

OUT OF SCOPE -
1. UI layer
2. Searching & FIltering the inventories
3. No update on warehouses (addition/ removal) - fixed at runtime
4. Get Product/ Get All Products
5. Alert delivery mechanism