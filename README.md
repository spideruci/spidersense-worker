This version used Python 3.5  

Before you run the program, replace the SQLALCHEMY_DATABASE_URI in src/workerServer.py to your own database connection and import spiderworker.sql to your database    

Because the .sql file is too large, you need to increase the size limit, use terminal to enter Mysql console, enter:
>show VARIABLES like '%max_allowed_packet%';  
>set global max_allowed_packet = 500\*1024\*1024; 

Then the size limit will be set up to 500MB 


After setting up the database, run 
>pip3 install -r requirement.txt
>python3 run.py


If run successful, go to 127.0.0.1:5000/graphql and test the graphQL query  

GraphQL's offcial tutorial is: https://graphql.org/learn/ 


