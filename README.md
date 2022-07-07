
# MiniTracker
This is a simple Http Server implementation of mini-tracker.
Before running, please first run install.sh. After installtion finishes, please run python3 ./mini\_tracker.py

The current version can be interacted with by sending HTTP requests, however it does not have good GUI support.
Sample requests:
1. Add an address
    curl -X POST http://localhost:5000/address/bc1q0sg9rdst255gtldsmcf8rk0764avqy2h2ksqs5
2. Get all addresses
    curl http://localhost:5000/address
3. Delete an address
    curl -X DELETE http://localhost:5000/address/bc1q0sg9rdst255gtldsmcf8rk0764avqy2h2ksqs5 
4. Get the balance of an address
    curl "http://localhost:5000/address/bc1q0sg9rdst255gtldsmcf8rk0764avqy2h2ksqs5/balance"
5. Get the transactions of an address (offset and limit are optional)
    curl "http://localhost:5000/address/bc1q0sg9rdst255gtldsmcf8rk0764avqy2h2ksqs5/txs?offset=0&limit=13"

NOTE:
    blockchain.io's cloudflare setting seems to be very strict on rate limiting, my program was throttled for long time after I simply sent three/four requests in five seconds. I had to use different IPs multiple times. Now I am adding a 5 second delay in between each request, but if there might still be some other rate limits. As such, I suggest use the above bitcoin address, which only has 2 transactions. Other addresses with more transactions could not be tested due to the possible rate limit.
