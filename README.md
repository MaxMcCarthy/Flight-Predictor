# Flight-Predictor

Description:

Flight Predictor will predict whether or not a flight gets delayed. It will also predict the user's wait time in security.

Usefulness:

Our application will help users put in their real flight data to predict whether it will get delayed. This will give users an idea of what to expect from their flight. Users will also be able to visualize heavy traffic airlines and times of the day. 

Dataset:

We will be getting our flight data from the Bureau of Transportation Statistics. We will keep track of a flight's airline, month, day of the month, day of the week, flight delay time, reason for delay (i.e. weather, security, etc), and origin and destination airports. We will be getting our airport wait time data from the US Customs and Border Protection Airport Wait Times dataset and will keep track of the origin airport, airline, average wait time, max wait time, and the hour of day.

Functionality:

i. Basic

- User Profiles
  - Add new flights
  - Specify airline, origin and destination airports, scheduled departure time, actual departure time, whether or not the flight was delayed
  - Display all of the user's flights 
  - Basic login authentication
  - User has ability to edit and delete flights 
- Flight Search
  - All flights similar to the user's specified flight based on airline, origin airport, date
  - Display to users the % chance that their flights will get delayed
- Wait Times
  - Display to users the predicted wait time at the airport on the specified day

ii. Advanced

- Predict whether a flight will get delayed
  - User inputs flight information
  - Use statistical methods such as permutation testing and cross-validation to select model for predicting delay time
  - Use best model to predict and display delay time
- Data Plots
  - The predicted delay for the user's flight's airline per hour
  - The predicted delay for the user's flight's airline for 3 +/- days from the specified date
  - The predicted delay for every airline on the user-specified date

Advanced Techniques

- Triggers
  - display a user's flight after it's been added to the database
- Prepared Statements
  - used to insert (i.e. INSERT INTO user VALUES(?, ?))
- Compound Statements
  - queries with multiple components
- Constraints
  - when creating tables (specify NOT NULL for fields)
- Views
  - get info on average wait times
  

Initial Project Demo

[YOUTUBE DEMO LINK](https://www.youtube.com/watch?v=afA4FcrephM&feature=youtu.be)
