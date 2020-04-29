# COVID-19_RMDS
Analysis and modeling on COVID-19 related data.
1) Data Source
    Disease data in MongoDB
    Mobility data in MongoDB & Git

2) Data Processing
    Clean: Remove null, NA
    Query/FIlter: US States only, US county only
    Merge tables according to place and time: df.left(["State","date"])

3) Feature Selection
    Refer to references and work from others: census data, mobility data, current epidemics
    Lag Effect Analysis on mobility data
      a) Create lagged mobility sequence
      b) Filter to places with more than 50 cases in total
      c) statistical analysis/qualitative comparison

4) 4E Model Building
    Equation: Derivative of Total cases in log scale ~ Lagged mobility data + days + population density + Aged Group >65
    Estimation: Algorithm: Random Forest Modeling, Gradient Boost, MLR
    Evalutaion: MAE, MAPE, RMSE
      Training/Testing: Randomly 1/4 for testing, 3/4 for training
    Execution: A model ready to output prediction based on independent variables

5) Production Data
    Prediction for all level of administration, and for future
