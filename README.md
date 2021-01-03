# League Tables Adjusted: Using underlying performance

The latest English Premier League based on [FiveThirtyEight](https://projects.fivethirtyeight.com/soccer-predictions/)'s game metrics.

#### Steps:

First, an average score of a match is calculated using the following formula.

**average-score** = average(xG, non-shot xG, adjusted-score)

Next, **Match Result** is decided based on the following conditions:

1. *Team 1* wins if average-score(team-1) - average-score(team-2) > **tolerance**
2. *Team 2* wins if average-score(team-2) - average-score(team-1) > **tolerance**
3. *Otherwise Draw*

**tolerance** = 0.2 (default)

A slider is made available on the webpage to change the above tolerance. A _larger_ tolerance ensures _more_ domination required for a win.

