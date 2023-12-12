import duckdb

# initiate the MotherDuck connection through a service token through
con = duckdb.connect('md:my_db?motherduck_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uIjoiaGF0cmlzeS5nbWFpbC5jb20iLCJlbWFpbCI6ImhhdHJpc3lAZ21haWwuY29tIiwidXNlcklkIjoiZDZhNWIzODYtOWRlZC00OWMxLTg1MzctMjBiMjUxMTc2MTgyIiwiaWF0IjoxNzAxMjE2MDg3LCJleHAiOjE3MzI3NzM2ODd9.CLcOUKJ5FA3ZjSP_6euRTv5lmVfHEyyL2Xs5a--jzq8', config = { "autoload_known_extensions": False }) 
local_con = duckdb.connect('/tmp/dbt.duckdb')
# connect to your MotherDuck database through 'md:mydatabase' or 'motherduck:mydatabase'
# if the database doesn't exist, MotherDuck creates it when you connect
# con = duckdb.connect('md:mydatabase')

# run a query to check verify that you are connected
con.sql("Select * from main.hacker_news limit 10;").show()

