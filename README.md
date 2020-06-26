## Python Simple Proxy Server

### Run and Test
- Run the server
    run `make` on the terminal.
- Navigate the server
    You can make a API request to the 
    ```sh
        http://localhost:8080/${sub_url}
    ```
    You can check the status of the server uptime and how many requests areprocessed so far. Go to 
    [http://localhost:8080/status](http://localhost:8000/status)

### Setting up env variable
- You should create a new `.env` file on `../compose/proxy/` and please take a look at `.env.example` to see which field you can configure.