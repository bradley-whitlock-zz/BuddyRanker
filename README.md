# BuddyRanker

## Inspiration
Friends playing squash looking for a way to rank themselves based on the outcomes of their individual games.

## Model: 
[Bradley-Terry](https://en.wikipedia.org/wiki/Bradley%E2%80%93Terry_model): One of the applications of this model is too predict the outcome of a comparison based on a pair of individuals in a population where data exists on the past results of these players. The more data that exists, the more accurate the model becomes.  

## Use Cases
Any 2 player game (ex. squash, cribbage) in which a winner exists and can be recorded on a game by game basis. Players should partake in several games to increase accuracy.

## How to Setup
1. Reccommended use with python virtualenv
2. Setup Sheets Access by creating [Google API Console](https://console.developers.google.com/apis/dashboard) account.
3. Download secret file (backup somewhere). Should have same fields as `secrets.json`.
4. Input data into `Scores` Google Sheets, [example data](https://docs.google.com/spreadsheets/d/1XbzocRHCA_xjH-l68kCLWV98r4jpqcSQM8XTk4fTfYQ/edit#gid=0)
5. Create `Rankings` page by executing run.sh (pip install dependencies if first run)
6. Optional: Setup Cronjob to update on daily/weekly basis.


### References
[Paper on Bradley Terry Model](http://sites.stat.psu.edu/~drh20/papers/bt.pdf)

[Similar implementation at Rubikloud](https://rubikloud.com/lab/building-a-table-tennis-ranking-model/)
